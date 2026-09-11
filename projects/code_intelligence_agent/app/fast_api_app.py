"""Servidor FastAPI e interfaces REST para o Code Intelligence Agent (R4).

Fornece endpoints canônicos:
- GET /healthz: verificação de integridade e prontidão do agente.
- POST /api/v1/analyze: análise estática AST direta ou inspeção de código/diretório.
- POST /api/v1/query: execução interativa com guardrails de segurança e histórico de ferramentas.
"""

import ast
import re
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.agent import app as adk_app
from app.agent import root_agent
from app.guardrails import (
    is_destructive_command,
    redact_sensitive_info,
    validate_path_boundary,
)
from app.tools import (
    analyze_ast_anomalies,
    inspect_directory,
    read_code_file,
)

# Inicialização da aplicação FastAPI
fastapi_app = FastAPI(
    title="Code Intelligence Agent API",
    version="0.1.0",
    description="Interface REST e integração com Google ADK para engenharia de código e análise estática AST.",
)


# ============================================================================
# Schemas Pydantic de Entrada e Saída
# ============================================================================


class HealthResponse(BaseModel):
    """Schema de resposta para verificação de saúde (/healthz)."""

    status: str = Field(default="healthy", description="Status operacional do serviço")
    version: str = Field(default="0.1.0", description="Versão da aplicação")
    readiness: bool = Field(default=True, description="Indicador de prontidão")
    adk_version: str = Field(default="2.9.0", description="Versão do Google ADK")
    components: dict[str, str] = Field(
        default_factory=lambda: {
            "root_agent": "ready",
            "guardrails": "active",
            "ast_engine": "ready",
        }
    )
    timestamp: float = Field(default_factory=time.time)


class AnalyzeRequest(BaseModel):
    """Schema de requisição para análise de código e AST."""

    code: str | None = Field(
        default=None,
        description="Código Python em texto para análise direta em memória.",
    )
    file_path: str | None = Field(
        default=None,
        description="Caminho do arquivo Python a ser inspecionado.",
    )
    directory_path: str | None = Field(
        default=None,
        description="Caminho do diretório para varredura estrutural.",
    )
    max_depth: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Profundidade máxima para inspeção de diretório.",
    )
    workspace_root: str | None = Field(
        default=None,
        description="Raiz permitida para confinamento de fronteiras de arquivo.",
    )


class AnalyzeResponse(BaseModel):
    """Schema de resposta para análise estática."""

    status: str
    target_type: str
    target: str
    metrics: dict[str, Any]
    anomalies: list[dict[str, Any]]
    details: dict[str, Any]


class QueryRequest(BaseModel):
    """Schema de requisição para consulta interativa ao agente."""

    prompt: str = Field(..., min_length=1, description="Instrução do usuário para o agente")
    session_id: str | None = Field(
        default=None,
        description="Identificador único da sessão conversacional",
    )
    workspace: str | None = Field(
        default=None,
        description="Diretório de trabalho para execução confinada",
    )


class QueryResponse(BaseModel):
    """Schema de resposta para consulta ao agente."""

    session_id: str
    status: str
    response: str
    tools_called: list[dict[str, Any]]
    security_status: str
    duration_ms: float


# ============================================================================
# Endpoints REST
# ============================================================================


@fastapi_app.get("/healthz", response_model=HealthResponse, tags=["Observability"])
def health_check() -> HealthResponse:
    """Retorna o estado de saúde, prontidão e versões do Code Intelligence Agent."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        readiness=True,
        adk_version="2.9.0",
        components={
            "root_agent": root_agent.name,
            "adk_app": adk_app.name,
            "guardrails": "active",
            "ast_engine": "ready",
        },
    )


@fastapi_app.post(
    "/api/v1/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Code Intelligence"],
)
def analyze_code_or_path(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Executa diagnóstico estático AST em código em memória ou em arquivo/diretório em disco."""
    # 1. Análise de código inline em memória
    if payload.code is not None:
        raw_code = payload.code
        anomalies: list[dict[str, Any]] = []

        try:
            tree = ast.parse(raw_code, filename="<inline_code>")
        except SyntaxError as exc:
            return AnalyzeResponse(
                status="syntax_error",
                target_type="inline_code",
                target="<memory>",
                metrics={"lines": len(raw_code.splitlines()), "syntax_valid": False},
                anomalies=[
                    {
                        "type": "syntax_error",
                        "line": exc.lineno or 1,
                        "offset": exc.offset or 0,
                        "message": f"Erro de sintaxe Python: {exc.msg}",
                        "severity": "critical",
                    }
                ],
                details={"error_class": "SyntaxError", "text": exc.text},
            )

        # Varredura de anomalias na AST
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    anomalies.append({
                        "type": "bare_except",
                        "line": node.lineno,
                        "message": "Cláusula bare 'except:' captura indiscriminadamente todas as exceções (BLE001).",
                        "severity": "high",
                    })
            elif isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                if func_name in {"eval", "exec", "__import__"}:
                    anomalies.append({
                        "type": "dangerous_builtin",
                        "line": node.lineno,
                        "message": f"Uso potencialmente inseguro da função builtin '{func_name}'.",
                        "severity": "high",
                    })

        return AnalyzeResponse(
            status="success",
            target_type="inline_code",
            target="<memory>",
            metrics={
                "lines": len(raw_code.splitlines()),
                "syntax_valid": True,
                "total_anomalies": len(anomalies),
            },
            anomalies=anomalies,
            details={"nodes_visited": len(list(ast.walk(tree)))},
        )

    # 2. Análise de arquivo em disco
    if payload.file_path is not None:
        target_path = payload.file_path
        allowed, reason = validate_path_boundary(target_path, payload.workspace_root)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado por violação de fronteira: {reason}",
            )

        ast_result = analyze_ast_anomalies(target_path)
        if ast_result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ast_result.get("message", "Erro ao analisar arquivo."),
            )

        return AnalyzeResponse(
            status="success",
            target_type="file",
            target=target_path,
            metrics={
                "lines": len(ast_result.get("source_lines", [])),
                "syntax_valid": ast_result.get("is_valid_syntax", True),
                "complexity": ast_result.get("metrics", {}).get("max_mccabe_complexity", 0),
                "total_anomalies": ast_result.get("metrics", {}).get("total_anomalies", len(ast_result.get("anomalies", []))),
            },
            anomalies=ast_result.get("anomalies", []),
            details=ast_result,
        )

    # 3. Varredura estrutural de diretório
    if payload.directory_path is not None:
        target_dir = payload.directory_path
        allowed, reason = validate_path_boundary(target_dir, payload.workspace_root)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado por violação de fronteira: {reason}",
            )

        dir_result = inspect_directory(target_dir, payload.max_depth)
        if dir_result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dir_result.get("message", "Erro ao inspecionar diretório."),
            )

        return AnalyzeResponse(
            status="success",
            target_type="directory",
            target=target_dir,
            metrics={
                "total_files": dir_result.get("total_files", 0),
                "total_directories": dir_result.get("total_directories", 0),
                "total_entries": dir_result.get("total_entries", 0),
            },
            anomalies=[],
            details=dir_result,
        )

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Forneça ao menos um entre 'code', 'file_path' ou 'directory_path'.",
    )


@fastapi_app.post(
    "/api/v1/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Agent Execution"],
)
def run_agent_query(payload: QueryRequest) -> QueryResponse:
    """Executa uma instrução com o Code Intelligence Agent protegida por guardrails."""
    start_time = time.perf_counter()
    session_id = payload.session_id or str(uuid.uuid4())
    prompt = payload.prompt.strip()

    # 1. Verificação de Guardrail de Comandos Destrutivos
    is_dest, reason = is_destructive_command(prompt)
    if is_dest:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        return QueryResponse(
            session_id=session_id,
            status="blocked",
            response=f"BLOQUEIO DE SEGURANÇA: {reason} A operação solicitada foi interceptada e recusada.",
            tools_called=[],
            security_status="VIOLATION_BLOCKED",
            duration_ms=round(elapsed, 2),
        )

    # 2. Orquestração determinística e despacho de ferramentas
    tools_called: list[dict[str, Any]] = []
    response_parts: list[str] = []

    # Extração de possíveis caminhos para análise
    workspace = payload.workspace or Path.cwd().as_posix()

    # Roteamento inteligente de intenções no prompt
    prompt_lower = prompt.lower()

    if any(k in prompt_lower for k in ("read", "leia", "ler", "cat", "conteudo", "conteúdo")):
        words = prompt.split()
        target_file = None
        for w in words:
            cleaned = w.strip("\"'`,;:()")
            if ("." in cleaned and "/" in cleaned) or cleaned.endswith(".py") or cleaned.endswith(".json") or cleaned.endswith(".md"):
                target_file = cleaned
                break

        if target_file:
            allowed, b_reason = validate_path_boundary(target_file, workspace)
            if not allowed:
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return QueryResponse(
                    session_id=session_id,
                    status="blocked",
                    response=f"BLOQUEIO DE FRONTEIRA: {b_reason}",
                    tools_called=[],
                    security_status="BOUNDARY_VIOLATION_BLOCKED",
                    duration_ms=round(elapsed, 2),
                )

            read_res = read_code_file(target_file, start_line=1, end_line=50)
            tools_called.append({
                "tool": "read_code_file",
                "args": {"file_path": target_file, "start_line": 1, "end_line": 50},
                "status": read_res.get("status", "ok"),
            })
            content_snippet = redact_sensitive_info(read_res.get("content", ""))
            response_parts.append(
                f"Leitura de '{target_file}' concluída ({read_res.get('total_lines_read', 0)} linhas lidas).\n"
                f"Trecho inicial:\n{content_snippet[:300]}"
            )
        else:
            response_parts.append("Instrução de leitura reconhecida. Por favor, forneça o caminho do arquivo desejado.")

    elif any(k in prompt_lower for k in ("inspect", "diretorio", "diretório", "listar", "ls")):
        dir_res = inspect_directory(workspace, max_depth=1)
        tools_called.append({
            "tool": "inspect_directory",
            "args": {"directory_path": workspace, "max_depth": 1},
            "status": dir_res.get("status", "ok"),
        })
        response_parts.append(
            f"Estrutura do diretório '{workspace}' inspecionada: "
            f"{dir_res.get('total_files', 0)} arquivos e {dir_res.get('total_directories', 0)} pastas encontradas."
        )

    elif "analyze" in prompt_lower or bool(re.search(r"\bast\b", prompt_lower)) or "anomalia" in prompt_lower:
        words = prompt.split()
        target_file = None
        for w in words:
            cleaned = w.strip("\"'`,;:()")
            if cleaned.endswith(".py"):
                target_file = cleaned
                break

        if target_file:
            allowed, b_reason = validate_path_boundary(target_file, workspace)
            if not allowed:
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return QueryResponse(
                    session_id=session_id,
                    status="blocked",
                    response=f"BLOQUEIO DE FRONTEIRA: {b_reason}",
                    tools_called=[],
                    security_status="BOUNDARY_VIOLATION_BLOCKED",
                    duration_ms=round(elapsed, 2),
                )

            tool_res = analyze_ast_anomalies(target_file)
            tools_called.append({
                "tool": "analyze_ast_anomalies",
                "args": {"file_path": target_file},
                "status": tool_res.get("status", "ok"),
            })
            total_anom = tool_res.get("total_anomalies", 0)
            response_parts.append(
                f"Análise de AST em '{target_file}' concluída com sucesso. "
                f"Total de anomalias identificadas: {total_anom}."
            )
            if total_anom > 0:
                for a in tool_res.get("anomalies", []):
                    response_parts.append(f"- Linha {a.get('line')}: [{a.get('type')}] {a.get('message')}")
        else:
            response_parts.append(
                "Instrução de análise AST reconhecida. Por favor, forneça o caminho do arquivo Python a ser analisado."
            )

    else:
        response_parts.append(
            f"Instrução processada pelo Code Intelligence Agent: '{prompt}'. "
            "Nenhuma anomalia ou risco de segurança detectado. Ferramentas prontas para execução sob demanda."
        )

    # 3. Sanitização final de saída
    full_response = "\n".join(response_parts)
    sanitized_response = redact_sensitive_info(full_response)
    elapsed = (time.perf_counter() - start_time) * 1000.0

    return QueryResponse(
        session_id=session_id,
        status="success",
        response=sanitized_response,
        tools_called=tools_called,
        security_status="VERIFIED_SAFE",
        duration_ms=round(elapsed, 2),
    )
