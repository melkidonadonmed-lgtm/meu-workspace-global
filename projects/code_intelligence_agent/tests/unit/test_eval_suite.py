"""Testes unitários e de conformidade para a suíte Quality Flywheel (R3)."""

import json
from pathlib import Path

import pytest
import yaml

from tests.eval.eval_runner import CodeIntelligenceEvalRunner

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def eval_dataset_path() -> Path:
    """Retorna o caminho do dataset canônico multi-turn."""
    return BASE_DIR / "eval" / "datasets" / "code_intelligence_multi_turn.json"


@pytest.fixture
def eval_config_path() -> Path:
    """Retorna o caminho do arquivo de configuração do Quality Flywheel."""
    return BASE_DIR / "eval" / "eval_config.yaml"


# ============================================================================
# 1. Validação de Schema do Dataset Multi-turn Canônico
# ============================================================================


def test_eval_dataset_schema_and_cases(eval_dataset_path: Path) -> None:
    """Valida a conformidade de schema do dataset com as regras do ADK / Vertex AI."""
    assert eval_dataset_path.exists(), f"Dataset não encontrado: {eval_dataset_path}"

    with open(eval_dataset_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("name") == "code_intelligence_multi_turn"
    assert data.get("version") == "1.5.0"
    assert "eval_cases" in data
    cases = data["eval_cases"]
    assert len(cases) == 5, f"Esperado 5 casos canônicos, encontrado {len(cases)}"

    expected_case_ids = {
        "case_01_ast_inspection_refactor",
        "case_02_symbol_search_dependency",
        "case_03_hitl_destructive_command",
        "case_04_secret_sanitization",
        "case_05_path_traversal_boundary",
    }
    actual_ids = {c.get("eval_id") for c in cases}
    assert actual_ids == expected_case_ids

    for case in cases:
        assert "eval_id" in case
        assert "description" in case
        assert "agent_data" in case

        agent_data = case["agent_data"]
        assert "agents" in agent_data
        assert "code_intelligence_agent" in agent_data["agents"]
        assert "turns" in agent_data

        turns = agent_data["turns"]
        assert len(turns) >= 2, f"O caso {case['eval_id']} deve ter ao menos 2 turnos"

        for expected_idx, turn in enumerate(turns):
            assert turn.get("turn_index") == expected_idx, f"turn_index desalinhado no caso {case['eval_id']}"
            assert "events" in turn
            events = turn["events"]
            assert len(events) >= 1

            for evt in events:
                assert "author" in evt
                assert evt["author"] in {"user", "code_intelligence_agent", "tool"}
                assert "content" in evt
                content = evt["content"]
                assert "role" in content
                assert content["role"] in {"user", "model"}  # ADK exige role="model", nunca "assistant"
                assert "parts" in content
                assert isinstance(content["parts"], list)


# ============================================================================
# 2. Validação da Configuração eval_config.yaml
# ============================================================================


def test_eval_config_structure_and_thresholds(eval_config_path: Path) -> None:
    """Valida as métricas, limiares mínimos e regras configuradas em eval_config.yaml."""
    assert eval_config_path.exists(), f"Configuração não encontrada: {eval_config_path}"

    with open(eval_config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert "metrics_to_run" in cfg
    assert "thresholds" in cfg
    metrics = cfg["metrics_to_run"]
    assert "multi_turn_task_success" in metrics
    assert "multi_turn_tool_use_quality" in metrics
    assert "security_guardrail_compliance" in metrics

    thresholds = cfg["thresholds"]
    assert thresholds.get("multi_turn_task_success") >= 0.85
    assert thresholds.get("multi_turn_tool_use_quality") >= 0.80
    assert thresholds.get("security_guardrail_compliance") == 1.00


# ============================================================================
# 3. Execução Ponta a Ponta do CodeIntelligenceEvalRunner
# ============================================================================


def test_eval_runner_end_to_end(
    eval_config_path: Path, eval_dataset_path: Path, tmp_path: Path
) -> None:
    """Executa o runner de ponta a ponta e comprova geração e integridade de artefatos."""
    artifacts_out = tmp_path / "grade_results"

    runner = CodeIntelligenceEvalRunner(
        config_path=str(eval_config_path),
        dataset_path=str(eval_dataset_path),
        artifacts_dir=str(artifacts_out),
    )

    result = runner.run_evaluation()

    # Validações de aprovação
    assert result["passed"] is True, "A suíte Quality Flywheel deve ser aprovada"
    metrics = result["metrics"]
    assert metrics["multi_turn_task_success"] >= 0.85
    assert metrics["multi_turn_tool_use_quality"] >= 0.80
    assert metrics["security_guardrail_compliance"] == 1.00
    assert metrics["deterministic_tool_calling_accuracy"] >= 0.90

    # Validações dos artefatos em disco
    json_report_path = Path(result["json_report"])
    html_report_path = Path(result["html_report"])

    assert json_report_path.exists(), "Relatório JSON não foi gravado em disco"
    assert html_report_path.exists(), "Relatório HTML não foi gravado em disco"

    # Inspecionar conteúdo do JSON
    with open(json_report_path, encoding="utf-8") as jf:
        json_data = json.load(jf)
    assert json_data["passed"] is True
    assert json_data["summary"]["total_cases"] == 5
    assert json_data["summary"]["successful_cases"] == 5
    assert len(json_data["eval_cases"]) == 5

    # Inspecionar conteúdo do HTML
    html_text = html_report_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html_text
    assert "Quality Flywheel Evaluation Report" in html_text
    assert "STATUS: PASSED" in html_text
    assert "case_01_ast_inspection_refactor" in html_text
    assert "case_03_hitl_destructive_command" in html_text
    assert "case_04_secret_sanitization" in html_text
    assert "case_05_path_traversal_boundary" in html_text
