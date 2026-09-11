"""Testes unitários e de robustez para o módulo de guardrails de segurança (R2).

Cobre exaustivamente:
1. Boundary Guard (validate_path_boundary): caminhos relativos, absolutos, traversal e arquivos protegidos.
2. Destructive Command Blocker (is_destructive_command): comandos perigosos em PowerShell, CMD, Bash, Git, SQL.
3. Credential & PII Redactor (redact_sensitive_info e sanitize_data): AIza keys, Bearer tokens, chaves privadas, CPF, emails.
4. ADK Lifecycle Interceptors (before_tool_guard_callback e after_tool_sanitizer_callback).
5. HITL Policy (evaluate_hitl_action): classificação em 3 níveis de risco Zero-Trust.
"""

from pathlib import Path
from typing import Any

from app.guardrails import (
    after_tool_sanitizer_callback,
    before_tool_guard_callback,
    evaluate_hitl_action,
    is_destructive_command,
    redact_sensitive_info,
    sanitize_data,
    validate_path_boundary,
)


class DummyTool:
    """Ferramenta fictícia para teste dos callbacks ADK."""

    def __init__(self, name: str = "test_code_tool") -> None:
        self.name = name


# ============================================================================
# 1. Testes do Boundary Guard (validate_path_boundary)
# ============================================================================


def test_validate_path_boundary_allowed_paths(tmp_path: Path) -> None:
    """Verifica que caminhos legítimos dentro do workspace são autorizados."""
    allowed_root = tmp_path / "workspace"
    allowed_root.mkdir()
    sub_dir = allowed_root / "src" / "modules"
    sub_dir.mkdir(parents=True)
    target_file = sub_dir / "app.py"
    target_file.write_text("print('hello')", encoding="utf-8")

    # Arquivo no subdiretório
    allowed, msg = validate_path_boundary(str(target_file), allowed_root=str(allowed_root))
    assert allowed is True
    assert msg == "ALLOWED"

    # O próprio diretório raiz
    allowed, msg = validate_path_boundary(str(allowed_root), allowed_root=str(allowed_root))
    assert allowed is True
    assert msg == "ALLOWED"

    # Caminho relativo a partir da raiz
    rel_path = "src/modules/app.py"
    allowed, msg = validate_path_boundary(str(allowed_root / rel_path), allowed_root=str(allowed_root))
    assert allowed is True
    assert msg == "ALLOWED"


def test_validate_path_boundary_path_traversal_blocked(tmp_path: Path) -> None:
    """Verifica que tentativas de escapar da raiz (Path Traversal) são sumariamente bloqueadas."""
    allowed_root = tmp_path / "project_root"
    allowed_root.mkdir()
    outside_dir = tmp_path / "outside_dir"
    outside_dir.mkdir()
    secret_file = outside_dir / "secret.txt"
    secret_file.write_text("super_secret", encoding="utf-8")

    # Caminho absoluto fora da raiz
    allowed, msg = validate_path_boundary(str(secret_file), allowed_root=str(allowed_root))
    assert allowed is False
    assert "BOUNDARY_VIOLATION" in msg

    # Traversal usando sequências '../'
    traversal_path = str(allowed_root / ".." / "outside_dir" / "secret.txt")
    allowed, msg = validate_path_boundary(traversal_path, allowed_root=str(allowed_root))
    assert allowed is False
    assert "BOUNDARY_VIOLATION" in msg

    # Traversal profundo
    deep_traversal = str(allowed_root / ".." / ".." / ".." / "Windows" / "System32")
    allowed, msg = validate_path_boundary(deep_traversal, allowed_root=str(allowed_root))
    assert allowed is False
    assert "BOUNDARY_VIOLATION" in msg


def test_validate_path_boundary_empty_and_invalid_inputs(tmp_path: Path) -> None:
    """Verifica tratamento determinístico para caminhos vazios ou somente espaços."""
    allowed_root = tmp_path / "workspace"
    allowed_root.mkdir()

    allowed, msg = validate_path_boundary("", allowed_root=str(allowed_root))
    assert allowed is False
    assert "INVALID_PATH" in msg

    allowed, msg = validate_path_boundary("   \t\n", allowed_root=str(allowed_root))
    assert allowed is False
    assert "INVALID_PATH" in msg


def test_validate_path_boundary_protected_files_blocked(tmp_path: Path) -> None:
    """Verifica que arquivos confidenciais (.env, chaves, certs) são bloqueados mesmo dentro do workspace."""
    allowed_root = tmp_path / "workspace"
    allowed_root.mkdir()

    protected_cases = [
        ".env",
        ".env.local",
        ".env.production",
        "credentials.json",
        "service_account_prod.json",
        "token.json",
        "id_rsa",
        "id_rsa.pub",
        "id_ed25519",
        "server.pem",
        "private.key",
        "cert.pfx",
    ]

    for file_name in protected_cases:
        target_path = allowed_root / file_name
        allowed, msg = validate_path_boundary(str(target_path), allowed_root=str(allowed_root))
        assert allowed is False, f"Deveria bloquear {file_name}"
        assert "PROTECTED_FILE" in msg


# ============================================================================
# 2. Testes do Destructive Command Blocker (is_destructive_command)
# ============================================================================


def test_is_destructive_command_blocks_all_dangerous_commands() -> None:
    """Testa a matriz completa de comandos de alto risco bloqueados por regex determinística."""
    destructive_commands = [
        # Linux / Bash
        "rm -rf /",
        "rm -rf node_modules",
        "rm -r src/build",
        "rm -fr /tmp/cache",
        "sudo rm -rf /etc",
        # PowerShell
        "Remove-Item -Path 'C:\\Project' -Recurse",
        "Remove-Item C:\\data -Recurse -Force",
        # Windows CMD
        "del /s /q C:\\workspace\\*",
        "erase /s temp_file.obj",
        "rmdir /s /q old_modules",
        "rd /s /q C:\\Users\\temp",
        # Git destrutivo
        "git reset --hard HEAD~1",
        "git reset --hard origin/main",
        "git clean -fdx",
        "git clean -f",
        "git push origin main --force",
        "git push -f origin feat",
        "git push --force-with-lease origin main",
        "git branch -D feature/login",
        # SQL destrutivo
        "DROP DATABASE production;",
        "DROP TABLE users CASCADE;",
        "TRUNCATE TABLE audit_log;",
        "truncate logs;",
        # Formatação e dispositivo de bloco
        "format c: /fs:ntfs",
        "dd if=/dev/zero of=/dev/sda bs=1M",
    ]

    for cmd in destructive_commands:
        is_destr, reason = is_destructive_command(cmd)
        assert is_destr is True, f"Falhou em detectar como destrutivo: {cmd}"
        assert "COMANDO_DESTRUTIVO_BLOQUEADO" in reason


def test_is_destructive_command_allows_safe_commands() -> None:
    """Verifica que comandos operacionais rotineiros e seguros não são falsamente bloqueados."""
    safe_commands = [
        "git status",
        "git log -n 5 --oneline",
        "git checkout -b feature/refactor",
        "git add .",
        "git commit -m 'feat: adicionar guardrails'",
        "npm run build",
        "uv run pytest",
        "uv run ruff check .",
        "python -m app.cli --help",
        "ls -la",
        "dir",
        "cat README.md",
        "echo 'Hello World'",
        "SELECT * FROM users WHERE active = 1;",
    ]

    for cmd in safe_commands:
        is_destr, reason = is_destructive_command(cmd)
        assert is_destr is False, f"Falso positivo gerado para comando seguro: {cmd}"
        assert "COMANDO_SEGURO" in reason

    # Comando vazio ou whitespace
    empty_destr, empty_reason = is_destructive_command("   ")
    assert empty_destr is False
    assert "COMANDO_VAZIO" in empty_reason


# ============================================================================
# 3. Testes do Redactor de Credenciais e PII (redact_sensitive_info)
# ============================================================================


def test_redact_sensitive_info_google_api_keys() -> None:
    """Verifica redação de Google API Keys (AIza...)."""
    text = "Erro na requisição usando API key AIzaSyD9876543210AbCdEfGhIjKlMnOpQrStU no endpoint."
    redacted = redact_sensitive_info(text)
    assert "AIza" not in redacted
    assert "[API_KEY_REDACTED]" in redacted


def test_redact_sensitive_info_bearer_tokens() -> None:
    """Verifica redação de Bearer tokens."""
    text = "Headers: {'Authorization': 'Bearer ya29.a0AfH6SMD89_AbCdEfGhIjKlMnOpQrStUvwxyz12345'}"
    redacted = redact_sensitive_info(text)
    assert "ya29" not in redacted
    assert "Bearer [TOKEN_REDACTED]" in redacted


def test_redact_sensitive_info_private_keys() -> None:
    """Verifica redação de blocos PEM de chave privada."""
    text = (
        "Certificado carregado:\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0AbCdEfGhIjKlMnOpQrStUvWxYz1234567890==\n"
        "-----END RSA PRIVATE KEY-----\n"
        "Fim do arquivo."
    )
    redacted = redact_sensitive_info(text)
    assert "MIIEowIBAAKCAQEA0" not in redacted
    assert "[PRIVATE_KEY_REDACTED]" in redacted


def test_redact_sensitive_info_cpf_and_email() -> None:
    """Verifica mascaramento de CPF e e-mails pessoais."""
    text = "O desenvolvedor Melki Donadon (CPF 123.456.789-00 ou 98765432100) pode ser contatado em dev@empresa.com.br."
    redacted = redact_sensitive_info(text)
    assert "123.456.789-00" not in redacted
    assert "98765432100" not in redacted
    assert "dev@empresa.com.br" not in redacted
    assert "[CPF_MASCARADO]" in redacted
    assert "[EMAIL_MASCARADO]" in redacted


def test_redact_sensitive_info_generic_secrets() -> None:
    """Verifica mascaramento de senhas literais em formato chave=valor."""
    text = "Configuração: password='minha_senha_super_secreta' e client_secret=\"chave_secreta_oauth_123\"."
    redacted = redact_sensitive_info(text)
    assert "minha_senha_super_secreta" not in redacted
    assert "chave_secreta_oauth_123" not in redacted
    assert "[SENHA_REDACTED]" in redacted


def test_sanitize_data_recursive_structure() -> None:
    """Verifica sanitização recursiva em estruturas complexas (dict, list, tuple)."""
    complex_data: dict[str, Any] = {
        "status": "success",
        "api_code": 200,
        "logs": [
            "User: admin@server.org",
            {"key": "AIzaSyD9876543210AbCdEfGhIjKlMnOpQrStU", "cpf": "111.222.333-44"},
        ],
        "tuple_info": ("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", 42),
    }

    sanitized = sanitize_data(complex_data)

    assert sanitized["api_code"] == 200
    assert sanitized["logs"][0] == "User: [EMAIL_MASCARADO]"
    assert sanitized["logs"][1]["key"] == "[API_KEY_REDACTED]"
    assert sanitized["logs"][1]["cpf"] == "[CPF_MASCARADO]"
    assert sanitized["tuple_info"][0] == "Bearer [TOKEN_REDACTED]"
    assert sanitized["tuple_info"][1] == 42


# ============================================================================
# 4. Testes dos Callbacks ADK (before_tool_guard e after_tool_sanitizer)
# ============================================================================


def test_before_tool_guard_callback_blocks_traversal_and_destructive(tmp_path: Path) -> None:
    """Verifica se before_tool_guard_callback bloqueia argumentos com traversal ou comando destrutivo."""
    dummy_tool = DummyTool("patch_tool")

    # 1. Bloqueia chamada com caminho fora da raiz permitida
    traversal_args = {"file_path": str(tmp_path / ".." / "outside" / "config.py")}
    intercept_res = before_tool_guard_callback(dummy_tool, traversal_args)
    assert intercept_res is not None
    assert intercept_res["status"] == "BLOCKED_BY_GUARDRAIL"
    assert intercept_res["error"] == "BOUNDARY_VIOLATION"
    assert intercept_res["argument"] == "file_path"

    # 2. Bloqueia chamada com comando destrutivo
    shell_tool = DummyTool("execute_shell")
    destructive_args = {"command": "rm -rf /var/log"}
    intercept_res_destr = before_tool_guard_callback(shell_tool, destructive_args)
    assert intercept_res_destr is not None
    assert intercept_res_destr["status"] == "BLOCKED_BY_GUARDRAIL"
    assert intercept_res_destr["error"] == "DESTRUCTIVE_COMMAND_BLOCKED"
    assert intercept_res_destr["argument"] == "command"


def test_before_tool_guard_callback_allows_safe_calls(tmp_path: Path) -> None:
    """Verifica se chamadas com argumentos seguros retornam None, permitindo a execução pelo ADK."""
    dummy_tool = DummyTool("read_tool")
    safe_file = tmp_path / "inside.py"
    safe_file.write_text("code = 1", encoding="utf-8")

    # Argumento de caminho seguro (dentro do cwd padrão ou seguro)
    safe_args = {"file_path": str(Path.cwd() / "pyproject.toml")}
    # pyproject.toml não é .env nem pem/key, é um arquivo válido
    intercept_res = before_tool_guard_callback(dummy_tool, safe_args)
    assert intercept_res is None

    # Chamada sem argumentos de caminho ou comando
    query_args = {"query": "def analyze", "max_results": 10}
    intercept_res_query = before_tool_guard_callback(dummy_tool, query_args)
    assert intercept_res_query is None


def test_after_tool_sanitizer_callback_redacts_response() -> None:
    """Verifica se after_tool_sanitizer_callback higieniza o retorno da ferramenta."""
    dummy_tool = DummyTool("search_tool")
    raw_response = {
        "status": "success",
        "matches": [
            "Found token: Bearer abcdef1234567890abcdef1234567890",
            "Owner contact: test.admin@google.com",
            "Key: AIzaSyA12345678901234567890123456789012",
        ],
        "count": 3,
    }

    sanitized_response = after_tool_sanitizer_callback(dummy_tool, {}, None, raw_response)

    assert "AIza" not in str(sanitized_response)
    assert "test.admin@google.com" not in str(sanitized_response)
    assert "[API_KEY_REDACTED]" in sanitized_response["matches"][2]
    assert "[EMAIL_MASCARADO]" in sanitized_response["matches"][1]
    assert "Bearer [TOKEN_REDACTED]" in sanitized_response["matches"][0]
    assert sanitized_response["count"] == 3


# ============================================================================
# 5. Testes da Política e Matriz HITL (evaluate_hitl_action)
# ============================================================================


def test_evaluate_hitl_action_levels() -> None:
    """Verifica classificação precisa dos 3 níveis de risco da matriz HITL."""
    # Nível 1: Leitura e análise estática
    lvl1_cases = [
        ("read_code_file", {"file_path": "app/tools.py"}),
        ("inspect_directory", {"directory_path": "app"}),
        ("analyze_ast_anomalies", {"file_path": "app/agent.py"}),
        ("search_files", {"query": "def run"}),
    ]
    for action, details in lvl1_cases:
        res = evaluate_hitl_action(action, details)
        assert res["risk_level"] == 1
        assert res["requires_hitl"] is False
        assert res["policy"] == "ALLOW_AUTOMATIC"

    # Nível 2: Mutação confinada e auditada
    lvl2_cases = [
        ("generate_unified_patch", {"file_path": "app/tools.py"}),
        ("patch", {"file_path": "app/agent.py"}),
        ("create_file", {"file_path": "app/new_module.py"}),
        ("modify_file", {"file_path": "tests/test_demo.py"}),
    ]
    for action, details in lvl2_cases:
        res = evaluate_hitl_action(action, details)
        assert res["risk_level"] == 2
        assert res["requires_hitl"] is False
        assert res["policy"] == "AUDITED_MUTATION"

    # Nível 3: Ações de alto risco ou comandos destrutivos explícitos (HITL obrigatório)
    lvl3_cases = [
        ("delete_file", {"file_path": "important.py"}),
        ("drop_database", {"db": "prod"}),
        ("format_disk", {"drive": "C:"}),
        ("git_force", {"branch": "main"}),
        # Ação com comando destrutivo embutido nos detalhes
        ("shell_execution", {"command": "rm -rf /app"}),
        # Ação com arquivo protegido embutido nos detalhes
        ("inspect_secret", {"file_path": ".env"}),
    ]
    for action, details in lvl3_cases:
        res = evaluate_hitl_action(action, details)
        assert res["risk_level"] == 3
        assert res["requires_hitl"] is True
        assert res["policy"] == "REQUIRE_CONFIRMATION"
