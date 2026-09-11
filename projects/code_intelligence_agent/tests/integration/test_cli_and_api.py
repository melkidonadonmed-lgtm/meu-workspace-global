"""Testes de Integração para CLI (Typer) e API REST (FastAPI) do Code Intelligence Agent."""

from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from app.cli import cli_app
from app.fast_api_app import fastapi_app

cli_runner = CliRunner()
client = TestClient(fastapi_app)


# ============================================================================
# 1. Testes de Integração da Interface CLI (code-intel)
# ============================================================================


def test_cli_help_shows_commands() -> None:
    """Verifica se o CLI exibe corretamente o menu de ajuda com os 4 comandos."""
    result = cli_runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "inspect" in result.output
    assert "serve" in result.output
    assert "eval" in result.output


def test_cli_inspect_python_file(tmp_path: Path) -> None:
    """Valida o comando `code-intel inspect` sobre um arquivo Python contendo anomalia."""
    test_file = tmp_path / "bad_code.py"
    test_file.write_text(
        "def process():\n"
        "    try:\n"
        "        x = 10\n"
        "    except:\n"
        "        pass\n",
        encoding="utf-8",
    )

    result = cli_runner.invoke(cli_app, ["inspect", str(test_file)])
    assert result.exit_code == 0
    assert "Diagnóstico AST" in result.output
    assert "bare_except" in result.output


def test_cli_inspect_directory(tmp_path: Path) -> None:
    """Valida o comando `code-intel inspect` sobre um diretório."""
    (tmp_path / "mod_a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "mod_b.py").write_text("y = 2\n", encoding="utf-8")

    result = cli_runner.invoke(cli_app, ["inspect", str(tmp_path)])
    assert result.exit_code == 0
    assert "Inspeção de Diretório" in result.output
    assert "Arquivos:" in result.output


def test_cli_inspect_blocks_boundary_violation(tmp_path: Path) -> None:
    """Valida que `code-intel inspect` bloqueia path traversal fora da raiz."""
    isolated_root = tmp_path / "isolated"
    isolated_root.mkdir()
    outside_file = tmp_path / "secret.py"
    outside_file.write_text("SECRET = 123\n", encoding="utf-8")

    result = cli_runner.invoke(
        cli_app,
        ["inspect", str(outside_file), "--workspace-root", str(isolated_root)],
    )
    assert result.exit_code != 0
    assert "ACESSO NEGADO" in result.output or "BOUNDARY_VIOLATION" in result.output


def test_cli_run_safe_instruction(tmp_path: Path) -> None:
    """Valida a execução de prompt seguro com o comando `code-intel run`."""
    result = cli_runner.invoke(
        cli_app,
        ["run", "Inspecione o diretório", "--workspace", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "inspect_directory" in result.output
    assert "SUCESSO" in result.output


def test_cli_run_blocks_destructive_command(tmp_path: Path) -> None:
    """Valida que o comando `code-intel run` intercepta comandos destrutivos."""
    result = cli_runner.invoke(
        cli_app,
        ["run", "rm -rf / --no-preserve-root", "--workspace", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "VIOLAÇÃO DE SEGURANÇA" in result.output
    assert "COMANDO_DESTRUTIVO_BLOQUEADO" in result.output


def test_cli_eval_execution() -> None:
    """Valida o comando `code-intel eval` disparando a suíte Quality Flywheel."""
    result = cli_runner.invoke(cli_app, ["eval"])
    assert result.exit_code == 0
    assert "PASS" in result.output
    assert "multi_turn_task_success" in result.output


# ============================================================================
# 2. Testes de Integração dos Endpoints FastAPI
# ============================================================================


def test_fastapi_healthz_endpoint() -> None:
    """Valida o endpoint GET /healthz."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert data["readiness"] is True
    assert data["adk_version"] == "2.9.0"
    assert "components" in data


def test_fastapi_analyze_inline_code_clean() -> None:
    """Valida POST /api/v1/analyze com código em memória limpo."""
    payload = {"code": "def soma(a: int, b: int) -> int:\n    return a + b\n"}
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["target_type"] == "inline_code"
    assert data["metrics"]["syntax_valid"] is True
    assert data["metrics"]["total_anomalies"] == 0


def test_fastapi_analyze_inline_code_anomalies() -> None:
    """Valida POST /api/v1/analyze identificando anomalia bare except e eval."""
    payload = {
        "code": (
            "def run_unsafe():\n"
            "    try:\n"
            "        eval('2+2')\n"
            "    except:\n"
            "        pass\n"
        )
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["metrics"]["total_anomalies"] >= 2
    types = [a["type"] for a in data["anomalies"]]
    assert "bare_except" in types
    assert "dangerous_builtin" in types


def test_fastapi_analyze_syntax_error() -> None:
    """Valida POST /api/v1/analyze com código com erro de sintaxe."""
    payload = {"code": "def broken(:\n"}
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "syntax_error"
    assert data["metrics"]["syntax_valid"] is False
    assert len(data["anomalies"]) == 1
    assert data["anomalies"][0]["type"] == "syntax_error"


def test_fastapi_analyze_file_path(tmp_path: Path) -> None:
    """Valida POST /api/v1/analyze com arquivo físico em disco."""
    test_file = tmp_path / "valid.py"
    test_file.write_text("x = 100\n", encoding="utf-8")

    payload = {"file_path": str(test_file), "workspace_root": str(tmp_path)}
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["target_type"] == "file"


def test_fastapi_analyze_file_path_boundary_violation(tmp_path: Path) -> None:
    """Valida POST /api/v1/analyze bloqueando arquivo fora do workspace com 403."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside_file = tmp_path / "outside.py"
    outside_file.write_text("y = 200\n", encoding="utf-8")

    payload = {"file_path": str(outside_file), "workspace_root": str(workspace)}
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 403
    assert "violação de fronteira" in response.json()["detail"].lower()


def test_fastapi_analyze_directory_path(tmp_path: Path) -> None:
    """Valida POST /api/v1/analyze com diretório físico."""
    (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
    payload = {"directory_path": str(tmp_path), "workspace_root": str(tmp_path)}
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_type"] == "directory"
    assert data["metrics"]["total_files"] >= 1


def test_fastapi_query_safe_instruction(tmp_path: Path) -> None:
    """Valida POST /api/v1/query com instrução permitida e ferramentas rastreadas."""
    payload = {
        "prompt": "Inspecione o diretório atual para verificar arquivos.",
        "workspace": str(tmp_path),
    }
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["security_status"] == "VERIFIED_SAFE"
    assert len(data["tools_called"]) >= 1
    assert data["tools_called"][0]["tool"] == "inspect_directory"


def test_fastapi_query_destructive_command_blocked() -> None:
    """Valida POST /api/v1/query bloqueando comando perigoso com feedback explicativo."""
    payload = {
        "prompt": "Por favor, execute: git reset --hard HEAD~1",
    }
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["security_status"] == "VIOLATION_BLOCKED"
    assert "BLOQUEIO DE SEGURANÇA" in data["response"]
    assert "git_reset_hard" in data["response"]
    assert len(data["tools_called"]) == 0


def test_fastapi_query_secret_sanitization(tmp_path: Path) -> None:
    """Valida POST /api/v1/query sanitizando credenciais ao ler arquivo."""
    secret_file = tmp_path / "auth_token.py"
    secret_file.write_text(
        "API_KEY = 'AIzaSyBN1234567890abcdef1234567890abcde'\n",
        encoding="utf-8",
    )

    payload = {
        "prompt": f"Leia o arquivo {secret_file.as_posix()}",
        "workspace": str(tmp_path),
    }
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "AIzaSy" not in data["response"]
    assert "[API_KEY_REDACTED]" in data["response"]
