"""Testes unitários determinísticos para as ferramentas de inteligência de código e AST."""

from pathlib import Path
from typing import Any

import pytest

from app.agent import app, root_agent, track_tool_state_callback
from app.tools import (
    analyze_ast_anomalies,
    generate_unified_patch,
    inspect_directory,
    read_code_file,
)


class MockToolContext:
    """Mock leve de ToolContext para validação de rastreamento de estado."""

    def __init__(self) -> None:
        self.state: dict[str, Any] = {}


class MockTool:
    """Mock de ferramenta para simular callbacks do ADK."""

    def __init__(self, name: str) -> None:
        self.name = name


# ============================================================================
# 1. Testes de inspect_directory
# ============================================================================


def test_inspect_directory_success_and_pruning(sample_codebase: Path) -> None:
    """Verifica varredura determinística, contagem e poda de pastas ignoradas (.git, __pycache__, .venv)."""
    result = inspect_directory(str(sample_codebase), max_depth=3)

    assert result["status"] == "success"
    assert result["total_files"] >= 4
    assert result["total_directories"] >= 1

    # Garante que pastas ignoradas foram podadas
    relative_paths = [e["relative_path"] for e in result["entries"]]
    for path in relative_paths:
        assert not path.startswith(".git")
        assert not path.startswith("__pycache__")
        assert not path.startswith(".venv")

    # Garante que arquivos e subdiretórios válidos foram encontrados
    assert any("clean_module.py" in p for p in relative_paths)
    assert any("subpackage" in p for p in relative_paths)
    assert any("sub_module.py" in p for p in relative_paths)


def test_inspect_directory_max_depth_zero(sample_codebase: Path) -> None:
    """Verifica que max_depth=0 lista apenas itens do diretório raiz sem recursão."""
    result = inspect_directory(str(sample_codebase), max_depth=0)

    assert result["status"] == "success"
    # Nenhum sub-item de subpackage deve ser incluído
    for entry in result["entries"]:
        assert entry["depth"] == 1
        assert "sub_module.py" not in entry["name"]


def test_inspect_directory_non_existent(tmp_path: Path) -> None:
    """Verifica tratamento de erro ao inspecionar diretório inexistente."""
    fake_path = tmp_path / "caminho_inexistente_12345"
    result = inspect_directory(str(fake_path), max_depth=2)

    assert result["status"] == "error"
    assert result["error"] == "DIRECTORY_NOT_FOUND"
    assert result["entries"] == []


# ============================================================================
# 2. Testes de read_code_file
# ============================================================================


def test_read_code_file_success(sample_codebase: Path) -> None:
    """Verifica leitura com linhas 1-indexed e fatiamento correto."""
    target = sample_codebase / "clean_module.py"
    result = read_code_file(str(target), start_line=3, end_line=6)

    assert result["status"] == "success"
    assert result["start_line"] == 3
    assert result["end_line"] == 6
    assert result["lines_returned"] == 4
    assert len(result["lines"]) == 4

    # Linha 3 deve ser a definição de somar
    assert result["lines"][0]["line_number"] == 3
    assert "def somar" in result["lines"][0]["content"]


def test_read_code_file_invalid_range_and_bounds(sample_codebase: Path) -> None:
    """Verifica validação de limites de linha inválidos."""
    target = sample_codebase / "clean_module.py"

    # start_line > end_line
    res_inv = read_code_file(str(target), start_line=10, end_line=5)
    assert res_inv["status"] == "error"
    assert res_inv["error"] == "INVALID_LINE_RANGE"

    # start_line além do fim do arquivo
    res_out = read_code_file(str(target), start_line=9999, end_line=10000)
    assert res_out["status"] == "error"
    assert res_out["error"] == "OUT_OF_BOUNDS"


def test_read_code_file_binary_and_missing(sample_codebase: Path) -> None:
    """Verifica rejeição de arquivos binários e arquivo não encontrado."""
    bin_target = sample_codebase / "binary.dat"
    res_bin = read_code_file(str(bin_target), start_line=1, end_line=10)
    assert res_bin["status"] == "error"
    assert res_bin["error"] == "BINARY_FILE"

    missing_target = sample_codebase / "nao_existe.py"
    res_mis = read_code_file(str(missing_target), start_line=1, end_line=10)
    assert res_mis["status"] == "error"
    assert res_mis["error"] == "FILE_NOT_FOUND"


def test_read_code_file_empty(sample_codebase: Path) -> None:
    """Verifica comportamento com arquivo vazio."""
    empty_target = sample_codebase / "empty.py"
    res = read_code_file(str(empty_target), start_line=1, end_line=10)
    assert res["status"] == "success"
    assert res["total_lines"] == 0
    assert res["content"] == ""


# ============================================================================
# 3. Testes de analyze_ast_anomalies
# ============================================================================


def test_analyze_ast_clean_file(sample_codebase: Path) -> None:
    """Verifica análise de arquivo sem anomalias."""
    target = sample_codebase / "clean_module.py"
    res = analyze_ast_anomalies(str(target))

    assert res["status"] == "success"
    assert res["is_valid_syntax"] is True
    assert res["syntax_error"] is None
    assert len(res["functions"]) == 2
    assert res["metrics"]["total_anomalies"] == 0
    assert res["metrics"]["max_mccabe_complexity"] == 1


def test_analyze_ast_syntax_error(sample_codebase: Path) -> None:
    """Verifica diagnóstico de arquivo com erro sintático."""
    target = sample_codebase / "syntax_error.py"
    res = analyze_ast_anomalies(str(target))

    assert res["status"] == "syntax_error"
    assert res["is_valid_syntax"] is False
    assert res["syntax_error"] is not None
    assert res["syntax_error"]["line"] >= 1
    assert len(res["anomalies"]) == 1
    assert res["anomalies"][0]["type"] == "syntax_error"


def test_analyze_ast_anomalies_detected(sample_codebase: Path) -> None:
    """Verifica detecção de bare except, generic except, McCabe > 10, função > 60 linhas e eval()."""
    target = sample_codebase / "anomalies_module.py"
    res = analyze_ast_anomalies(str(target))

    assert res["status"] == "success"
    assert res["is_valid_syntax"] is True

    anomaly_types = {a["type"] for a in res["anomalies"]}
    assert "bare_except" in anomaly_types
    assert "generic_except" in anomaly_types
    assert "high_complexity" in anomaly_types
    assert "long_function" in anomaly_types
    assert "dangerous_call" in anomaly_types
    assert "mutable_default_arg" in anomaly_types

    # Validação do cálculo de McCabe
    mccabe_anomaly = next(a for a in res["anomalies"] if a["type"] == "high_complexity")
    assert mccabe_anomaly["function_name"] == "funcao_complexa"
    assert mccabe_anomaly["complexity"] > 10

    # Validação de função longa
    long_fn_anomaly = next(a for a in res["anomalies"] if a["type"] == "long_function")
    assert long_fn_anomaly["function_name"] == "funcao_longa_monolitica"
    assert long_fn_anomaly["lines_count"] > 60


def test_analyze_ast_non_python_and_missing(sample_codebase: Path) -> None:
    """Verifica rejeição de arquivos que não são Python e arquivos inexistentes."""
    txt_file = sample_codebase / "notes.txt"
    res_txt = analyze_ast_anomalies(str(txt_file))
    assert res_txt["status"] == "error"
    assert res_txt["error"] == "NOT_PYTHON_FILE"

    missing = sample_codebase / "ghost.py"
    res_mis = analyze_ast_anomalies(str(missing))
    assert res_mis["status"] == "error"
    assert res_mis["error"] == "FILE_NOT_FOUND"


# ============================================================================
# 4. Testes de generate_unified_patch
# ============================================================================


def test_generate_unified_patch_success(tmp_path: Path) -> None:
    """Verifica aplicação bem sucedida de patch com unified diff e persistência em disco."""
    test_file = tmp_path / "patch_target.py"
    test_file.write_text("def calcular(x):\n    return x * 2\n", encoding="utf-8")

    orig_snippet = "    return x * 2"
    repl_snippet = "    # Refatorado para elevar ao quadrado\n    return x ** 2"

    res = generate_unified_patch(str(test_file), orig_snippet, repl_snippet)

    assert res["status"] == "applied"
    assert res["applied"] is True
    assert res["changes_made"] is True
    assert "+    return x ** 2" in res["diff"]

    # Conteúdo no disco deve estar atualizado
    updated_content = test_file.read_text(encoding="utf-8")
    assert "return x ** 2" in updated_content
    assert "return x * 2" not in updated_content


def test_generate_unified_patch_dry_run_ast_rejection(tmp_path: Path) -> None:
    """GARANTIA DE INTEGRIDADE: Verifica que patch com erro sintático é rejeitado e arquivo não é alterado."""
    test_file = tmp_path / "ast_guard_target.py"
    original_code = "def processar(x):\n    return x + 10\n"
    test_file.write_text(original_code, encoding="utf-8")

    orig_snippet = "    return x + 10"
    # Snippet com erro sintático fatal em Python
    broken_snippet = "    return x + + %%% INVALID SYNTAX"

    res = generate_unified_patch(str(test_file), orig_snippet, broken_snippet)

    assert res["status"] == "rejected"
    assert res["applied"] is False
    assert res["changes_made"] is False
    assert res["error"] == "SYNTAX_ERROR"
    assert "violação de integridade sintática" in res["message"].lower()

    # O arquivo no disco DEVE permanecer estritamente inalterado!
    disk_content = test_file.read_text(encoding="utf-8")
    assert disk_content == original_code


def test_generate_unified_patch_target_not_found_and_ambiguous(tmp_path: Path) -> None:
    """Verifica rejeição quando snippet não existe ou ocorre mais de uma vez."""
    test_file = tmp_path / "ambiguous_target.py"
    test_file.write_text("a = 1\na = 1\n", encoding="utf-8")

    # Não encontrado
    res_not_found = generate_unified_patch(str(test_file), "b = 99", "b = 100")
    assert res_not_found["status"] == "error"
    assert res_not_found["error"] == "TARGET_NOT_FOUND"

    # Ambíguo (ocorre 2 vezes)
    res_ambiguous = generate_unified_patch(str(test_file), "a = 1", "a = 2")
    assert res_ambiguous["status"] == "error"
    assert res_ambiguous["error"] == "AMBIGUOUS_MATCH"


def test_generate_unified_patch_no_op(tmp_path: Path) -> None:
    """Verifica que substituição idêntica resulta em no_op."""
    test_file = tmp_path / "noop_target.py"
    test_file.write_text("x = 10\n", encoding="utf-8")

    res = generate_unified_patch(str(test_file), "x = 10", "x = 10")
    assert res["status"] == "no_op"
    assert res["applied"] is False
    assert res["changes_made"] is False


# ============================================================================
# 5. Testes do Agente ADK e State Tracking
# ============================================================================


def test_adk_agent_configuration_and_state_tracking() -> None:
    """Valida a configuração do root_agent, App e o callback de rastreamento de estado."""
    # Validações do root_agent
    assert root_agent.name == "code_intelligence_agent"
    assert root_agent.model == "gemini-3.8-flash"
    assert len(root_agent.tools) == 4
    assert root_agent.generate_content_config.temperature == pytest.approx(0.1)

    # Validação do App (Convenção ADK: name="app")
    assert app.name == "app"
    assert app.root_agent is root_agent

    # Validação do callback de rastreamento de estado
    mock_ctx = MockToolContext()
    mock_tool = MockTool("analyze_ast_anomalies")
    fake_args = {"file_path": "foo/bar.py"}
    fake_response = {
        "status": "success",
        "anomalies": [{"type": "bare_except", "line": 42}],
    }

    track_tool_state_callback(mock_tool, fake_args, mock_ctx, fake_response)

    assert "tool_execution_history" in mock_ctx.state
    assert len(mock_ctx.state["tool_execution_history"]) == 1
    assert mock_ctx.state["tool_execution_history"][0]["tool"] == "analyze_ast_anomalies"
    assert "detected_anomalies" in mock_ctx.state
    assert len(mock_ctx.state["detected_anomalies"]) == 1
    assert mock_ctx.state["detected_anomalies"][0]["type"] == "bare_except"
