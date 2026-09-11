"""Testes unitários para o módulo de automação headless do Antigravity CLI."""

import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.agy_stream_session import AntigravitySession

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_docs_and_scripts_exist():
    """Garante que a documentação e os scripts do modo headless estão presentes no workspace."""
    doc_path = REPO_ROOT / "docs" / "antigravity-headless-mode.md"
    ps_script_path = REPO_ROOT / "scripts" / "run-agy-headless.ps1"
    py_script_path = REPO_ROOT / "scripts" / "agy_stream_session.py"

    assert doc_path.exists(), "Documentação docs/antigravity-headless-mode.md não encontrada."
    assert ps_script_path.exists(), "Script scripts/run-agy-headless.ps1 não encontrado."
    assert py_script_path.exists(), "Script scripts/agy_stream_session.py não encontrado."

    # Verifica se a documentação contém as seções essenciais
    doc_text = doc_path.read_text(encoding="utf-8")
    assert "Modo Headless" in doc_text
    assert "--output-format" in doc_text
    assert "--input-format stream-json" in doc_text


def test_antigravity_session_init():
    """Valida inicialização e parâmetros da classe AntigravitySession."""
    session = AntigravitySession(
        model="gemini-3.8-flash-high",
        effort="high",
        timeout_seconds=60.0,
        extra_args=["--dangerously-skip-permissions"],
    )
    assert session.model == "gemini-3.8-flash-high"
    assert session.effort == "high"
    assert session.timeout_seconds == 60.0
    assert "--dangerously-skip-permissions" in session.extra_args
    assert session.conversation_id is None


def test_antigravity_session_ndjson_lifecycle():
    """Testa o ciclo de vida completo de mensagens NDJSON simulando a saída do processo CLI."""
    mock_proc = MagicMock()
    
    # Simula o fluxo: 1) evento init, 2) evento step_update, 3) evento result
    ndjson_output = (
        '{"event":"init","conversation_id":"test-uuid-1234"}\n'
        '{"event":"step_update","step_update":{"step_index":1,"state":"DONE"}}\n'
        '{"event":"result","result":{"status":"SUCCESS","response":"Resposta teste","num_turns":1}}\n'
    )
    mock_proc.stdout = io.StringIO(ndjson_output)
    mock_proc.stdin = io.StringIO()
    mock_proc.wait.return_value = 0

    with (
        patch("shutil.which", return_value="agy.exe"),
        patch("subprocess.Popen", return_value=mock_proc),
        AntigravitySession() as session,
    ):
        assert session.conversation_id == "test-uuid-1234"

        result = session._ask_direct("Olá modelo")
        assert result.get("status") == "SUCCESS"
        assert result.get("response") == "Resposta teste"
        assert result.get("num_turns") == 1

        # Verifica se a mensagem de entrada foi devidamente serializada para o stdin
        mock_proc.stdin.seek(0)
        written = mock_proc.stdin.read()
        sent_msg = json.loads(written.strip())
        assert sent_msg.get("event") == "user"
        assert sent_msg.get("message", {}).get("content") == "Olá modelo"
