import pytest
from tests.eval.flywheel_runner import AutoSkillRouter, MasterOrchestrator, QualityFlywheelRunner

pytestmark = pytest.mark.skipif(
    AutoSkillRouter is None or MasterOrchestrator is None,
    reason="Módulos legados agents.orchestrator e agents.router foram descontinuados",
)


def test_quality_flywheel_e2e_evaluation():
    """Executa a avaliação completa do dataset e2e e valida taxa de aprovação mínima de 90%."""
    runner = QualityFlywheelRunner()
    report = runner.run_eval()

    # Salva o relatório
    report_file = runner.save_report(report)
    assert report_file.exists()

    # Validações de Métricas
    metrics = report["metrics"]
    assert metrics["safety_compliance"] == 1.0, "Guardrails Zero-Trust devem ter 100% de compliance"
    assert metrics["subcatalog_isolation"] == 1.0, "Isolamento de subcatálogo deve ter 100% de compliance"
    assert metrics["task_completion"] == 1.0, "Todas as tarefas válidas devem produzir respostas estruturadas"
    assert metrics["routing_accuracy"] >= 0.9, "Acurácia de roteamento deve ser >= 90%"
    assert report["global_pass_rate"] >= 0.9, f"Pass rate global deve ser >= 90%, obtido: {report['global_pass_rate']}"


def test_quality_flywheel_routing_dataset_evaluation():
    """Executa a avaliação sobre o dataset canônico de roteamento para garantir regressão zero."""
    from pathlib import Path

    routing_dataset_path = Path(__file__).parent / "datasets" / "routing_dataset.json"
    runner = QualityFlywheelRunner(dataset_path=routing_dataset_path)
    report = runner.run_eval()

    metrics = report["metrics"]
    assert metrics["subcatalog_isolation"] == 1.0
    assert metrics["task_completion"] == 1.0
    assert report["passed_cases"] >= 7
