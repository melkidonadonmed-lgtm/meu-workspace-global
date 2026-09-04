"""Subagente Especialista em Análise Contínua de Código, Anti-Drift e Sincronização de Contexto."""

import ast
import os
import re

from pydantic import BaseModel, Field

from shared.logger import get_logger

logger = get_logger("CodeConsistencySpecialist")


class CodeContract(BaseModel):
    """Contrato técnico ou assinatura de interface acordada no ecossistema."""

    name: str = Field(description="Nome do símbolo, classe, função, schema ou rota")
    contract_type: str = Field(
        description="Tipo de contrato: pydantic_schema, function, class, fastapi_route, mcp_tool"
    )
    file_path: str = Field(description="Caminho do arquivo de origem")
    signature: str = Field(description="Assinatura, tipos de entrada/saída ou formato esperado")
    description: str = Field(default="", description="Propósito e regra do contrato")


class CodeDriftIssue(BaseModel):
    """Problema de desvio de arquitetura, incompatibilidade ou convenção quebrado."""

    severity: str = Field(
        default="warning",
        description="Nível de gravidade: error (impede execução), warning (desvio de padrão), info"
    )
    category: str = Field(
        description="Categoria: syntax_error, type_incompatibility, contract_drift, convention_violation"
    )
    file_path: str = Field(default="unknown", description="Arquivo onde o desvio foi detectado")
    description: str = Field(description="Explicação detalhada do desvio ou incompatibilidade")
    suggestion: str = Field(description="Ação corretiva recomendada")


class CodeSyncSnapshot(BaseModel):
    """Snapshot consolidado do estado do código para propagação entre todos os subagentes."""

    step_index: int = Field(description="Passo atual do fluxo multi-turn")
    is_sync_turn: bool = Field(description="Indica se a verificação periódica (a cada X steps) disparou")
    status: str = Field(
        default="aligned",
        description="Status de alinhamento: aligned (sem desvios), drift_detected (com alertas), blocked (com erros graves)"
    )
    active_contracts: dict[str, CodeContract] = Field(
        default_factory=dict,
        description="Contratos ativos registrados para consulta dos demais agentes"
    )
    drift_issues: list[CodeDriftIssue] = Field(
        default_factory=list,
        description="Lista de desvios ou incompatibilidades encontrados"
    )
    files_in_scope: list[str] = Field(
        default_factory=list,
        description="Arquivos tocados ou sob análise no ciclo atual"
    )
    shared_directives_for_agents: list[str] = Field(
        default_factory=list,
        description="Diretrizes imediatas de sincronização que todos os subagentes devem obedecer"
    )


class CodeConsistencySpecialistAgent:
    """Subagente especialista em análise de código, validação de contratos e prevenção de code drift.

    Monitora o contexto multi-turn, executa auditorias a cada X steps e sintetiza
    o estado atual em snapshots compartilhados entre todos os agentes.
    """

    def __init__(
        self,
        default_sync_interval: int = 3,
        api_key: str | None = None,
        model_name: str = "gemini-3.7-flash",
    ):
        self.default_sync_interval = default_sync_interval
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.registered_contracts: dict[str, CodeContract] = {}
        self.known_files: set[str] = set()
        self.client = None
        self._init_client()

    def _init_client(self) -> None:
        """Inicializa o cliente Google GenAI se disponível (opcional para enriquecimento)."""
        if self.api_key and self.api_key != "mock_key_12345":
            try:
                from google import genai

                self.client = genai.Client(api_key=self.api_key)
                logger.info("Cliente Google GenAI configurado no CodeConsistencySpecialist.")
            except Exception as e:  # noqa: BLE001 - fallback para validação estática local
                logger.warning(f"Google GenAI não inicializado no CodeConsistencySpecialist: {e}")

    def should_trigger_sync(self, step_index: int, interval: int | None = None) -> bool:
        """Verifica se o step atual deve disparar a sincronização periódica (a cada X steps)."""
        step_gap = interval or self.default_sync_interval
        if step_gap <= 0:
            return True
        return (step_index > 0) and (step_index % step_gap == 0)

    def register_contract(self, contract: CodeContract) -> None:
        """Registra um contrato formal no catálogo ativo do sentinela."""
        self.registered_contracts[contract.name] = contract

    def audit_syntax_and_ast(self, code: str, file_path: str = "snippet.py") -> list[CodeDriftIssue]:
        """Verifica sintaxe Python e extrai nós de AST para validar conformidade."""
        issues: list[CodeDriftIssue] = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append(
                CodeDriftIssue(
                    severity="error",
                    category="syntax_error",
                    file_path=file_path,
                    description=f"Erro de sintaxe Python na linha {e.lineno}: {e.msg}",
                    suggestion="Corrija a sintaxe antes de propagar o código para os demais agentes.",
                )
            )
            return issues

        # Varredura por desvios de convenção
        for node in ast.walk(tree):
            # Validação: Proibir exceto Exception genérico sem justificativa ou noqa
            if isinstance(node, ast.ExceptHandler) and (
                node.type is None or (isinstance(node.type, ast.Name) and node.type.id == "Exception")
            ):
                # Verifica se o código contém justificativa ou comentário BLE001
                    lines = code.splitlines()
                    line_idx = max(0, node.lineno - 1)
                    line_text = lines[line_idx] if line_idx < len(lines) else ""
                    if "BLE001" not in line_text and "noqa" not in line_text:
                        issues.append(
                            CodeDriftIssue(
                                severity="warning",
                                category="convention_violation",
                                file_path=file_path,
                                description=(
                                    f"Cláusula 'except Exception' na linha {node.lineno} sem '# noqa: BLE001' "
                                    "ou justificativa explícita (regra de convenção AGENTS.md)."
                                ),
                                suggestion="Especifique exceções concretas ou adicione '# noqa: BLE001' com justificativa.",
                            )
                        )

        return issues

    def check_contract_compatibility(
        self,
        proposed_symbols: dict[str, str],
        file_path: str = "unknown"
    ) -> list[CodeDriftIssue]:
        """Compara assinaturas propostas contra os contratos já estabelecidos."""
        drift_issues: list[CodeDriftIssue] = []
        for sym_name, proposed_sig in proposed_symbols.items():
            if sym_name in self.registered_contracts:
                existing = self.registered_contracts[sym_name]
                if existing.signature != proposed_sig:
                    drift_issues.append(
                        CodeDriftIssue(
                            severity="error",
                            category="contract_drift",
                            file_path=file_path,
                            description=(
                                f"Incompatibilidade de contrato detectada no símbolo '{sym_name}'. "
                                f"Contrato existente: '{existing.signature}'. "
                                f"Assinatura proposta: '{proposed_sig}'."
                            ),
                            suggestion=(
                                f"Alinhe a assinatura com o contrato estabelecido em {existing.file_path} "
                                "ou atualize o contrato formalmente com aprovação."
                            ),
                        )
                    )
        return drift_issues

    def extract_symbols_from_code(self, code: str, file_path: str = "snippet.py") -> dict[str, CodeContract]:
        """Extrai classes, funções e modelos do código para registrar no catálogo de contratos."""
        extracted: dict[str, CodeContract] = {}
        try:
            tree = ast.parse(code)
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    # Identifica se é Pydantic BaseModel
                    is_pydantic = any(
                        (isinstance(b, ast.Name) and b.id == "BaseModel") or
                        (isinstance(b, ast.Attribute) and b.attr == "BaseModel")
                        for b in node.bases
                    )
                    ctype = "pydantic_schema" if is_pydantic else "class"
                    extracted[node.name] = CodeContract(
                        name=node.name,
                        contract_type=ctype,
                        file_path=file_path,
                        signature=f"class {node.name}",
                        description=ast.get_docstring(node) or "",
                    )
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    arg_names = [a.arg for a in node.args.args]
                    sig = f"def {node.name}({', '.join(arg_names)})"
                    extracted[node.name] = CodeContract(
                        name=node.name,
                        contract_type="function",
                        file_path=file_path,
                        signature=sig,
                        description=ast.get_docstring(node) or "",
                    )
        except SyntaxError:
            pass
        return extracted

    def analyze_step(
        self,
        step_index: int,
        code_snippets: list[tuple[str, str]] | None = None,
        files_modified: list[str] | None = None,
        context_summary: str = "",
        force_sync: bool = False,
        sync_interval: int | None = None,
    ) -> CodeSyncSnapshot:
        """Executa a inspeção de consistência no step atual e emite o snapshot de alinhamento.

        Args:
            step_index: Número do passo/turno atual na sessão.
            code_snippets: Lista de tuplas `(file_path, code_text)` submetidas no step.
            files_modified: Lista de arquivos alterados.
            context_summary: Resumo do contexto ou instrução do usuário.
            force_sync: Se True, força a geração do snapshot mesmo fora do intervalo.
            sync_interval: Sobrescreve o intervalo padrão se informado.

        Returns:
            CodeSyncSnapshot contendo status, desvios e diretrizes compartilhadas.
        """
        interval = sync_interval or self.default_sync_interval
        is_sync_turn = force_sync or self.should_trigger_sync(step_index, interval)

        files = list(files_modified or [])
        snippets = list(code_snippets or [])
        for f, _ in snippets:
            if f not in files:
                files.append(f)
        self.known_files.update(files)

        all_issues: list[CodeDriftIssue] = []

        # 1. Auditoria sintática e contratos
        for file_path, code in snippets:
            syntax_issues = self.audit_syntax_and_ast(code, file_path)
            all_issues.extend(syntax_issues)

            if not syntax_issues:
                symbols = self.extract_symbols_from_code(code, file_path)
                proposed_signatures = {name: c.signature for name, c in symbols.items()}
                compat_issues = self.check_contract_compatibility(proposed_signatures, file_path)
                all_issues.extend(compat_issues)

                # Se não há quebra, registra/atualiza os novos contratos
                for contract in symbols.values():
                    self.register_contract(contract)

        # 2. Verificação de desvio arquitetural por regex no contexto
        if context_summary and re.search(r"\b(print\(|console\.log)\b", context_summary):
            all_issues.append(
                CodeDriftIssue(
                        severity="info",
                        category="convention_violation",
                        file_path="context",
                        description="Uso detectado de prints diretos. Recomenda-se uso de 'shared.logger'.",
                        suggestion="Substitua print() por logger.info/warning para observabilidade.",
                    )
                )

        # 3. Determinação de Status
        has_errors = any(i.severity == "error" for i in all_issues)
        has_warnings = any(i.severity == "warning" for i in all_issues)
        if has_errors:
            status = "blocked"
        elif has_warnings:
            status = "drift_detected"
        else:
            status = "aligned"

        # 4. Síntese de Diretrizes Compartilhadas para outros agentes
        shared_directives: list[str] = []
        if is_sync_turn:
            shared_directives.append(
                f"[CHECKPOINT STEP {step_index}] Todos os subagentes devem manter compatibilidade com os contratos ativos."
            )
            if self.registered_contracts:
                contracts_summary = ", ".join(self.registered_contracts.keys())
                shared_directives.append(f"Contratos protegidos e vigentes: {contracts_summary}.")
            if files:
                shared_directives.append(f"Arquivos em escopo direto: {', '.join(files)}.")
            if has_errors:
                shared_directives.append("ATENÇÃO: Existem erros bloqueantes de compatibilidade que devem ser corrigidos.")

        snapshot = CodeSyncSnapshot(
            step_index=step_index,
            is_sync_turn=is_sync_turn,
            status=status,
            active_contracts=self.registered_contracts,
            drift_issues=all_issues,
            files_in_scope=sorted(self.known_files),
            shared_directives_for_agents=shared_directives,
        )

        if is_sync_turn:
            logger.info(
                f"🔄 [Step {step_index}] Sincronização periódica concluída. Status: '{status}' "
                f"({len(all_issues)} issues, {len(self.registered_contracts)} contratos ativos)."
            )

        return snapshot

    def format_prompt_injection_for_peers(self, snapshot: CodeSyncSnapshot) -> str:
        """Formata o snapshot em XML estruturado para injeção no prompt de outros agentes."""
        lines = [
            "<code_context_sync>",
            f"  <step_index>{snapshot.step_index}</step_index>",
            f"  <status>{snapshot.status}</status>",
        ]
        if snapshot.files_in_scope:
            lines.append(f"  <files_in_scope>{', '.join(snapshot.files_in_scope)}</files_in_scope>")

        if snapshot.active_contracts:
            lines.append("  <active_contracts>")
            for name, c in snapshot.active_contracts.items():
                lines.append(f"    <contract name=\"{name}\" type=\"{c.contract_type}\">{c.signature}</contract>")
            lines.append("  </active_contracts>")

        if snapshot.drift_issues:
            lines.append("  <drift_alerts>")
            for issue in snapshot.drift_issues:
                lines.append(
                    f"    <issue severity=\"{issue.severity}\" category=\"{issue.category}\">"
                    f"{issue.description} (Sugestão: {issue.suggestion})</issue>"
                )
            lines.append("  </drift_alerts>")

        if snapshot.shared_directives_for_agents:
            lines.append("  <shared_directives>")
            for directive in snapshot.shared_directives_for_agents:
                lines.append(f"    <directive>{directive}</directive>")
            lines.append("  </shared_directives>")

        lines.append("</code_context_sync>")
        return "\n".join(lines)

