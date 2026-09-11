"""Módulo de Guardrails de Segurança Zero-Trust, Interceptadores ADK e Políticas HITL (R2).

Fornece defesas em profundidade para agentes autônomos de engenharia de código:
1. Boundary Guard: confinamento rigoroso de caminhos e bloqueio de path traversal / arquivos protegidos.
2. Destructive Command Blocker: regex determinística de alta performance para barrar comandos destrutivos de SO.
3. Credential & PII Redactor: sanitização e redação de credenciais, chaves de API, segredos e dados pessoais.
4. ADK Lifecycle Interceptors: callbacks before_tool e after_tool para interceptação ativa.
5. HITL Policy: matriz de decisão em três níveis de risco (Automático, Mutação Auditada, HITL Obrigatório).
"""

import re
from pathlib import Path
from typing import Any

# ============================================================================
# 1. Expressões Regulares Pré-Compiladas para Comandos Destrutivos
# ============================================================================

DESTRUCTIVE_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    # Remoção forçada e recursiva (Linux, macOS, Git Bash)
    (
        "rm_rf",
        re.compile(r"(?i)\brm\s+-[a-z]*r[a-z]*\b|\brm\s+.*-[a-z]*r[a-z]*\b"),
        "Remoção recursiva de diretórios via comando rm",
    ),
    # PowerShell Remove-Item recursivo
    (
        "powershell_remove_item_recurse",
        re.compile(r"(?i)\bRemove-Item\b.*-Recurse"),
        "Remoção recursiva PowerShell (Remove-Item -Recurse)",
    ),
    # Windows CMD del /s /q ou erase /s
    (
        "cmd_del_recursive",
        re.compile(r"(?i)\b(?:del|erase)\s+.*\/[sS]\b|\b(?:del|erase)\s+\/[sS]\b"),
        "Exclusão recursiva de arquivos via prompt Windows (del /s)",
    ),
    # Windows CMD rmdir /s ou rd /s
    (
        "cmd_rmdir_recursive",
        re.compile(r"(?i)\b(?:rmdir|rd)\s+.*\/[sS]\b|\b(?:rmdir|rd)\s+\/[sS]\b"),
        "Exclusão recursiva de árvore de diretórios via prompt Windows (rmdir /s)",
    ),
    # Git reset hard
    (
        "git_reset_hard",
        re.compile(r"(?i)\bgit\s+reset\s+--hard\b"),
        "Redefinição destrutiva do repositório Git com perda de commits (git reset --hard)",
    ),
    # Git clean -fdx / -f
    (
        "git_clean_force",
        re.compile(r"(?i)\bgit\s+clean\s+-[a-z]*f[a-z]*\b"),
        "Exclusão forçada de arquivos não rastreados no Git (git clean -fdx)",
    ),
    # Git push force
    (
        "git_push_force",
        re.compile(r"(?i)\bgit\s+push\b.*(?:\s--force\b|\s-f\b|\s--force-with-lease\b)"),
        "Sobrescrita forçada do histórico do repositório remoto (git push --force)",
    ),
    # Git branch delete force
    (
        "git_branch_force_delete",
        re.compile(r"(?i)\bgit\s+branch\s+.*-[dD]\b"),
        "Exclusão forçada de branch Git (git branch -D)",
    ),
    # Destruição SQL
    (
        "sql_drop",
        re.compile(r"(?i)\bdrop\s+(?:database|schema|table|view)\b"),
        "Destruição de estrutura relacional de banco de dados (DROP DATABASE/TABLE)",
    ),
    (
        "sql_truncate",
        re.compile(r"(?i)\btruncate\s+(?:table\s+)?\w+\b"),
        "Esvaziamento irrecuperável de tabela de dados (TRUNCATE TABLE)",
    ),
    # Formatação de volume de disco
    (
        "disk_format",
        re.compile(r"(?i)\bformat\s+[a-z]:"),
        "Formatação de volume de armazenamento (format [drive]:)",
    ),
    # Escrita direta destrutiva em dispositivos de bloco
    (
        "dd_block_write",
        re.compile(r"(?i)\bdd\s+.*of=(?:/dev/|[a-z]:)"),
        "Escrita direta destrutiva em dispositivo físico de bloco (dd)",
    ),
]

# ============================================================================
# 2. Padrões Regex Pré-Compilados para Credenciais e PII
# ============================================================================

REDACTION_RULES: list[tuple[str, re.Pattern[str], str]] = [
    # Google API Key (AIza...)
    (
        "google_api_key",
        re.compile(r"AIza[0-9A-Za-z-_]{30,45}"),
        "[API_KEY_REDACTED]",
    ),
    # Bearer Tokens
    (
        "bearer_token",
        re.compile(r"(?i)Bearer\s+[a-zA-Z0-9_\-\.]{20,}"),
        "Bearer [TOKEN_REDACTED]",
    ),
    # Chaves Privadas PEM/OpenSSH/RSA/EC
    (
        "private_key",
        re.compile(r"-----BEGIN (?:[A-Z0-9_-]+ )?PRIVATE KEY-----[\s\S]+?-----END (?:[A-Z0-9_-]+ )?PRIVATE KEY-----"),
        "[PRIVATE_KEY_REDACTED]",
    ),
    # CPF (com ou sem formatação pontuada)
    (
        "cpf",
        re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
        "[CPF_MASCARADO]",
    ),
    # E-mails
    (
        "email",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "[EMAIL_MASCARADO]",
    ),
]

# Padrão genérico para segredos explícitos chave=valor (ex: password='xxx', api_key="yyy")
GENERIC_SECRET_PATTERN = re.compile(
    r"""(?i)\b(password|passwd|secret|api_secret|client_secret)\s*([:=])\s*(['"])[^'"]{6,}\3"""
)

# Arquivos estritamente protegidos cujo acesso é proibido mesmo dentro da raiz
PROTECTED_FILE_NAMES: set[str] = {
    ".env",
    "credentials.json",
    "token.json",
}

PROTECTED_FILE_EXTENSIONS: set[str] = {
    ".pem",
    ".key",
    ".pfx",
    ".p12",
}

# Chaves de argumentos de ferramentas a serem inspecionadas pelo interceptador
PATH_ARGUMENT_KEYS: set[str] = {
    "file_path",
    "directory_path",
    "target_path",
    "target_file",
    "path",
    "source_path",
    "dest_path",
    "destination_path",
}

COMMAND_ARGUMENT_KEYS: set[str] = {
    "command",
    "command_line",
    "cmd",
    "CommandLine",
    "script",
    "shell_command",
}


# ============================================================================
# 3. Funções Principais de Guardrail
# ============================================================================


def validate_path_boundary(target_path: str, allowed_root: str | None = None) -> tuple[bool, str]:
    """Valida se o caminho especificado reside estritamente dentro da raiz permitida e não viola arquivos protegidos.

    Normaliza caminhos com Path(p).resolve().as_posix().lower() para evitar bypass no Windows
    (case-insensitivity e variações de barras / e \\).

    Args:
        target_path: Caminho alvo (relativo ou absoluto) a ser verificado.
        allowed_root: Caminho da raiz permitida. Se None, utiliza o diretório de trabalho atual (cwd).

    Returns:
        Tupla (is_allowed: bool, reason: str).
    """
    if not target_path or not str(target_path).strip():
        return False, "INVALID_PATH: O caminho não pode ser vazio ou conter apenas espaços em branco."

    if allowed_root is not None and str(allowed_root).strip():
        root_path = Path(allowed_root).resolve()
    else:
        root_path = Path.cwd().resolve()

    try:
        resolved_target = Path(target_path).resolve()
    except Exception as e:
        return False, f"PATH_RESOLUTION_ERROR: Não foi possível resolver o caminho '{target_path}': {e}"

    # Normalização robusta Windows (POSIX + lowercase)
    target_posix = resolved_target.as_posix().lower()
    root_posix = root_path.as_posix().lower()

    # Checagem de confinamento de diretório (Path Traversal prevention)
    is_inside = (target_posix == root_posix) or target_posix.startswith(root_posix + "/")
    if not is_inside:
        return (
            False,
            f"BOUNDARY_VIOLATION: O alvo '{target_path}' resolve para '{resolved_target.as_posix()}', "
            f"que está fora da raiz permitida '{root_path.as_posix()}'.",
        )

    # Checagem de arquivos protegidos
    target_name = resolved_target.name.lower()
    if (
        target_name in PROTECTED_FILE_NAMES
        or target_name.startswith(".env.")
        or (target_name.startswith("service_account") and target_name.endswith(".json"))
        or target_name.startswith("id_rsa")
        or target_name.startswith("id_ed25519")
        or resolved_target.suffix.lower() in PROTECTED_FILE_EXTENSIONS
    ):
        return (
            False,
            f"PROTECTED_FILE: Acesso ao arquivo protegido '{resolved_target.name}' "
            "é expressamente bloqueado por política de segurança.",
        )

    return True, "ALLOWED"


def is_destructive_command(command_line: str) -> tuple[bool, str]:
    """Detecta de forma determinística e de alta performance comandos potencialmente destrutivos para o SO.

    Args:
        command_line: Linha de comando a ser inspecionada.

    Returns:
        Tupla (is_destructive: bool, reason: str).
    """
    if not command_line or not str(command_line).strip():
        return False, "COMANDO_VAZIO: Nenhuma instrução fornecida."

    cmd_text = str(command_line).strip()

    for rule_id, pattern, desc in DESTRUCTIVE_PATTERNS:
        if pattern.search(cmd_text):
            return (
                True,
                f"COMANDO_DESTRUTIVO_BLOQUEADO [{rule_id}]: {desc}.",
            )

    return False, "COMANDO_SEGURO: Nenhuma operação destrutiva detectada."


def redact_sensitive_info(text: str) -> str:
    """Sanitiza e redige chaves de API, credenciais, segredos e dados pessoais (PII) de um texto.

    Args:
        text: Texto bruto de entrada.

    Returns:
        Texto sanitizado com tokens de mascaramento padronizados.
    """
    if not isinstance(text, str):
        return text

    sanitized = text

    # Aplica substituições por regras pré-compiladas
    for _, pattern, replacement in REDACTION_RULES:
        sanitized = pattern.sub(replacement, sanitized)

    # Aplica mascaramento de segredos genéricos (password='...', etc.)
    sanitized = GENERIC_SECRET_PATTERN.sub(r"\1\2\3[SENHA_REDACTED]\3", sanitized)

    return sanitized


def sanitize_data(data: Any) -> Any:
    """Varre recursivamente dicionários, listas e tuplas, aplicando redact_sensitive_info em todas as strings."""
    if isinstance(data, str):
        return redact_sensitive_info(data)
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    if isinstance(data, list):
        return [sanitize_data(item) for item in data]
    if isinstance(data, tuple):
        return tuple(sanitize_data(item) for item in data)
    if isinstance(data, set):
        return {sanitize_data(item) for item in data}
    return data


# ============================================================================
# 4. Interceptadores de Ciclo de Vida do Google ADK
# ============================================================================


def before_tool_guard_callback(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any = None,
) -> dict[str, Any] | None:
    """Interceptador pré-execução de ferramentas no Google ADK.

    Inspeciona argumentos em busca de violações de fronteira de diretório (Path Traversal /
    arquivos protegidos) ou comandos destrutivos de sistema operacional. Se uma violação for detectada,
    bloqueia a chamada retornando um dicionário sintético descritivo (sem disparar a ferramenta).

    Args:
        tool: Objeto da ferramenta proposta.
        args: Dicionário de argumentos passados para a ferramenta.
        tool_context: Contexto de execução da ferramenta no ADK (opcional).

    Returns:
        None se a chamada for segura; dict com status 'BLOCKED_BY_GUARDRAIL' se for bloqueada.
    """
    if not isinstance(args, dict):
        return None

    tool_name = getattr(tool, "name", getattr(tool, "__name__", str(tool)))

    # Inspeciona argumentos de caminho
    for key, value in args.items():
        if key in PATH_ARGUMENT_KEYS and isinstance(value, str):
            is_allowed, reason = validate_path_boundary(value)
            if not is_allowed:
                return {
                    "status": "BLOCKED_BY_GUARDRAIL",
                    "error": "BOUNDARY_VIOLATION",
                    "message": f"Chamada à ferramenta '{tool_name}' bloqueada pelo Boundary Guard: {reason}",
                    "tool": tool_name,
                    "argument": key,
                    "value": value,
                }

    # Inspeciona argumentos de linha de comando
    for key, value in args.items():
        if key in COMMAND_ARGUMENT_KEYS and isinstance(value, str):
            is_destructive, reason = is_destructive_command(value)
            if is_destructive:
                return {
                    "status": "BLOCKED_BY_GUARDRAIL",
                    "error": "DESTRUCTIVE_COMMAND_BLOCKED",
                    "message": f"Chamada à ferramenta '{tool_name}' bloqueada pelo Destructive Command Blocker: {reason}",
                    "tool": tool_name,
                    "argument": key,
                    "value": value,
                }

    return None


def after_tool_sanitizer_callback(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any,
    tool_response: Any,
) -> Any:
    """Interceptador pós-execução de ferramentas no Google ADK.

    Varre o retorno da ferramenta e aplica redação em qualquer credencial, chave de API
    ou dado pessoal sensível (PII) antes de retornar os dados ao modelo.

    Args:
        tool: Objeto da ferramenta executada.
        args: Argumentos utilizados.
        tool_context: Contexto da ferramenta no ADK.
        tool_response: Retorno original da ferramenta.

    Returns:
        Estrutura de dados devidamente sanitizada.
    """
    return sanitize_data(tool_response)


# ============================================================================
# 5. Política e Avaliação HITL (Human-in-the-Loop)
# ============================================================================


def evaluate_hitl_action(
    action_type: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classifica uma ação operacional em três níveis de risco conforme a política HITL Zero-Trust.

    Níveis de risco:
    - Nível 1: Operação de leitura segura ou análise estática (execução automática autorizada).
    - Nível 2: Mutação confinada dentro do projeto com validação prévia (autorizada com auditoria).
    - Nível 3: Ação de alto risco ou comando potencialmente destrutivo (exige confirmação humana explícita).

    Args:
        action_type: Identificador da ação (ex: 'read_code_file', 'patch', 'shell_command').
        details: Metadados contextuais adicionais (argumentos, caminho do arquivo, comando).

    Returns:
        Dicionário com o nível de risco (1, 2 ou 3), status requires_hitl, política e justificativa.
    """
    details = details or {}
    act_lower = str(action_type).lower().strip()

    # Verificação de comando destrutivo embutido nos detalhes
    cmd = details.get("command") or details.get("command_line") or details.get("cmd") or details.get("CommandLine")
    if cmd and isinstance(cmd, str):
        is_destr, reason = is_destructive_command(cmd)
        if is_destr:
            return {
                "risk_level": 3,
                "action_type": action_type,
                "requires_hitl": True,
                "policy": "REQUIRE_CONFIRMATION",
                "reason": f"Comando destrutivo detectado nos detalhes da ação: {reason}",
                "details": details,
            }

    # Verificação de fronteira de caminho nos detalhes
    file_p = (
        details.get("file_path")
        or details.get("directory_path")
        or details.get("target_file")
        or details.get("path")
    )
    if file_p and isinstance(file_p, str):
        is_allowed, reason = validate_path_boundary(file_p)
        if not is_allowed:
            return {
                "risk_level": 3,
                "action_type": action_type,
                "requires_hitl": True,
                "policy": "REQUIRE_CONFIRMATION",
                "reason": f"Alvo de arquivo viola fronteira ou arquivo protegido: {reason}",
                "details": details,
            }

    # Mapeamento de ações de Nível 3 (Alto Risco)
    level_3_actions = {
        "destructive_command",
        "delete_file",
        "delete_directory",
        "drop_database",
        "truncate_table",
        "git_force",
        "format_disk",
        "modify_root_config",
        "modify_env",
        "high_risk",
    }
    if act_lower in level_3_actions:
        return {
            "risk_level": 3,
            "action_type": action_type,
            "requires_hitl": True,
            "policy": "REQUIRE_CONFIRMATION",
            "reason": "Ação operacional de alto risco classificada; requer autorização humana explícita (HITL).",
            "details": details,
        }

    # Mapeamento de ações de Nível 2 (Mutações Confinadas)
    level_2_actions = {
        "patch",
        "apply_patch",
        "generate_unified_patch",
        "create_file",
        "write_code",
        "modify_file",
        "propose_patch",
    }
    if act_lower in level_2_actions:
        return {
            "risk_level": 2,
            "action_type": action_type,
            "requires_hitl": False,
            "policy": "AUDITED_MUTATION",
            "reason": "Modificação confinada e validada no escopo do projeto; autorizada com auditoria obrigatória.",
            "details": details,
        }

    # Nível 1: Leitura e análise segura (Padrão)
    return {
        "risk_level": 1,
        "action_type": action_type,
        "requires_hitl": False,
        "policy": "ALLOW_AUTOMATIC",
        "reason": "Operação de leitura segura ou análise estática confinada; execução automática autorizada.",
        "details": details,
    }
