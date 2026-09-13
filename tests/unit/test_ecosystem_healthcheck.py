"""Testes unitários para o módulo de diagnóstico do Hub Central (ecosystem_healthcheck.py)."""

import json
import sys
from pathlib import Path

# Adicionar caminho dos scripts do hub central para importação
HUB_SCRIPTS_DIR = Path(r"C:\Users\melki\.gemini\scripts")
if str(HUB_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(HUB_SCRIPTS_DIR))

import ecosystem_healthcheck as eh


def test_check_json_file(tmp_path):
    """Valida leitura e validação de JSON sintático."""
    valid_file = tmp_path / "valid.json"
    valid_file.write_text(json.dumps({"status": "ok"}), encoding="utf-8")
    ok, msg = eh.check_json_file(valid_file)
    assert ok is True
    assert "JSON válido" in msg

    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{broken json", encoding="utf-8")
    ok, msg = eh.check_json_file(invalid_file)
    assert ok is False
    assert "JSON inválido" in msg

    missing_file = tmp_path / "missing.json"
    ok, msg = eh.check_json_file(missing_file)
    assert ok is False
    assert "não encontrado" in msg


def test_check_python_ast(tmp_path):
    """Valida análise da árvore sintática abstrata (AST)."""
    valid_py = tmp_path / "script.py"
    valid_py.write_text("def hello():\n    return 42\n", encoding="utf-8")
    ok, msg = eh.check_python_ast(valid_py)
    assert ok is True
    assert "100% válida" in msg

    invalid_py = tmp_path / "broken.py"
    invalid_py.write_text("def def broken::", encoding="utf-8")
    ok, msg = eh.check_python_ast(invalid_py)
    assert ok is False
    assert "Erro de sintaxe AST" in msg


def test_test_hook_contract():
    """Valida o teste dinâmico de contrato de hook com pre_tool_guard.py."""
    hook_path = Path(r"C:\Users\melki\.gemini\scripts\hooks\pre_tool_guard.py")
    if not hook_path.exists():
        return

    mock_payload = {
        "toolCall": {
            "name": "run_command",
            "args": {"CommandLine": "dir"},
        }
    }
    ok, msg = eh.check_hook_contract(hook_path, mock_payload, "decision")
    assert ok is True
    assert "Contrato de execução válido" in msg


def test_run_hub_healthcheck_returns_healthy():
    """Valida execução completa da varredura determinística do Hub Central."""
    report = eh.run_hub_healthcheck()
    assert report.total_checks >= 10
    assert report.is_healthy is True
    assert report.failed_checks == 0
