"""Ferramentas (FunctionTools) do Google ADK para auditoria e resolução de projetos.

Consome o Deep Module ProjectTargetResolver e o CodeConsistencySpecialistAgent.
Todas as ferramentas seguem as regras estritas do ADK para geração de schema do Gemini:
1. Type hints obrigatórios em todos os argumentos.
2. Sem valores padrão (default values) nos parâmetros para o schema.
3. Docstrings descritivas com blocos Args e Returns.
4. Retornos estruturados em dict serializáveis em JSON.
"""

from pathlib import Path
from typing import Any, Dict
from agents.project_resolver import ProjectTargetResolver
from agents.specialized.code_consistency_specialist import CodeConsistencySpecialistAgent
from shared.logger import get_logger

logger = get_logger("AuditAgentTools")
consistency_specialist = CodeConsistencySpecialistAgent()


def list_available_projects() -> Dict[str, Any]:
    """Lista todos os projetos canônicos registrados no ecossistema e seus metadados.

    Consulta a Single Source of Truth (SSoT) em projects.json e junctions ativas.

    Returns:
        Dicionário com a lista de projetos, seus aliases, portas e caminhos físicos.
    """
    try:
        projects = ProjectTargetResolver.list_all_projects()
        return {
            "status": "success",
            "count": len(projects),
            "projects": projects,
        }
    except Exception as exc:
        logger.error(f"Erro ao listar projetos: {exc}")
        return {"status": "error", "message": str(exc)}


def scan_project_structure(project_name_or_path: str, max_depth: int) -> Dict[str, Any]:
    """Inspeciona a estrutura de pastas, tecnologias detectadas e manifestos de um projeto.

    Args:
        project_name_or_path: Nome do projeto (ex: 'pcm', 'canvas_ide', 'WAOE') ou caminho relativo/absoluto.
        max_depth: Profundidade máxima de diretórios a inspecionar (ex: 2 ou 3).

    Returns:
        Dicionário com contagem de arquivos, árvore simplificada e stacks detectadas (React, TypeScript, Vite, Python, etc.).
    """
    try:
        resolved = ProjectTargetResolver.resolve_project(project_name_or_path)
        scan_result = ProjectTargetResolver.scan_directory(
            resolved.target_path, max_depth=max_depth
        )
        return {
            "status": "success",
            "project_name": resolved.name,
            "display_name": resolved.display_name,
            "resolved_path": str(resolved.target_path),
            "is_junction": resolved.is_junction,
            "tech_stack": resolved.tech_stack,
            "port": resolved.port,
            "detected_stacks": scan_result.get("detected_stacks", []),
            "total_files": scan_result.get("files_count", 0),
            "total_directories": scan_result.get("directories_count", 0),
            "tree_preview": scan_result.get("tree", [])[:30],
        }
    except Exception as exc:
        logger.error(f"Erro na varredura do projeto '{project_name_or_path}': {exc}")
        return {
            "status": "error",
            "project_query": project_name_or_path,
            "message": str(exc),
        }


def inspect_code_contracts(file_path: str) -> Dict[str, Any]:
    """Analisa um arquivo Python via AST e extrai contratos de código (classes, funções, schemas Pydantic).

    Args:
        file_path: Caminho do arquivo de código a ser inspecionado.

    Returns:
        Dicionário contendo os contratos de código e assinaturas encontradas.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return {
            "status": "error",
            "file_path": file_path,
            "message": f"Arquivo não encontrado: {file_path}",
        }

    try:
        content = p.read_text(encoding="utf-8")
        issues = consistency_specialist.audit_syntax_and_ast(content, file_path=p.name)
        return {
            "status": "success",
            "file_path": str(p),
            "total_issues": len(issues),
            "issues": [issue.model_dump() for issue in issues],
        }
    except Exception as exc:
        return {
            "status": "error",
            "file_path": file_path,
            "message": f"Falha na análise AST: {str(exc)}",
        }


def check_code_drift(file_path: str) -> Dict[str, Any]:
    """Verifica se há erros de sintaxe ou violações de convenção de código (AST anti-drift).

    Args:
        file_path: Caminho do arquivo a ser validado contra padrões arquiteturais.

    Returns:
        Dicionário indicando se o código está alinhado ou com desvios arquiteturais.
    """
    p = Path(file_path)
    if not p.exists():
        return {"status": "error", "message": f"Arquivo inexistente: {file_path}"}

    try:
        code = p.read_text(encoding="utf-8")
        issues = consistency_specialist.audit_syntax_and_ast(code, file_path=p.name)
        status = "aligned" if not issues else "drift_detected"
        return {
            "status": status,
            "file_path": str(p),
            "issues_count": len(issues),
            "issues": [i.model_dump() for i in issues],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
