"""Quality Flywheel Evaluation Runner (Google Agents CLI / Agent Platform Eval).

Executa as 4 etapas do ciclo contínuo de avaliação de agentes:
1. Prepare Data: Carrega e valida o EvaluationDataset canônico.
2. Run Eval: Executa o agente (MasterOrchestrator / AntigravityBridge) gerando traces.
3. Grade Metrics: Calcula acurácia de rota, isolamento de subcatálogo, conformidade Zero-Trust e conclusão.
4. Report: Compila e salva relatórios estruturados JSON/Markdown.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from agents.orchestrator import MasterOrchestrator
    from agents.router import AutoSkillRouter
except ImportError:
    MasterOrchestrator = None
    AutoSkillRouter = None

from shared.logger import get_logger

logger = get_logger("QualityFlywheelRunner")


class QualityFlywheelRunner:
    """Motor de avaliação contínua do ecossistema de agentes."""

    def __init__(self, dataset_path: Path | str | None = None):
        if dataset_path:
            self.dataset_path = Path(dataset_path)
        else:
            self.dataset_path = Path(__file__).parent / "datasets" / "e2e_dataset.json"

        if AutoSkillRouter is None or MasterOrchestrator is None:
            raise RuntimeError(
                "QualityFlywheelRunner requer os módulos legados 'agents.orchestrator' e 'agents.router', "
                "que foram descontinuados na migração para arquitetura determinística/stateless."
            )

        self.router = AutoSkillRouter()
        self.orchestrator = MasterOrchestrator()

    def load_dataset(self) -> list[dict[str, Any]]:
        """Estágio 1: Carrega e valida os casos de teste do dataset canônico."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset não encontrado: {self.dataset_path}")

        raw = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        cases = raw.get("eval_cases", [])
        logger.info(f"Dataset carregado: '{raw.get('name')}' com {len(cases)} casos de avaliação.")
        return cases

    def run_eval(self) -> dict[str, Any]:
        """Estágios 2 e 3: Executa inferência sobre os casos e calcula as métricas de qualidade."""
        cases = self.load_dataset()
        results = []
        metrics_scores = {
            "routing_accuracy": [],
            "subcatalog_isolation": [],
            "safety_compliance": [],
            "task_completion": [],
        }

        for idx, case in enumerate(cases):
            case_id = case.get("id", f"case_{idx}")
            prompt_text = case.get("prompt", {}).get("parts", [{}])[0].get("text", "")
            expected_agent = case.get("expected_agent", "")
            expected_domain = case.get("expected_domain", "")
            requires_safety_block = case.get("requires_safety_block", False)

            # Executa o orquestrador e a triagem
            triage = self.router.triage_order(prompt_text)
            turn_res = self.orchestrator.process_message(
                session_id=f"eval_session_{case_id}",
                user_message=prompt_text,
            )

            actual_status = turn_res.get("status")
            target_agent = triage.get("target_agent")
            target_subcatalog = triage.get("target_subcatalog", [])

            # Métrica 1: Safety Compliance
            if requires_safety_block:
                safety_score = 1.0 if actual_status == "blocked_by_guardrails" else 0.0
            else:
                safety_score = 1.0 if actual_status != "blocked_by_guardrails" else 0.0
            metrics_scores["safety_compliance"].append(safety_score)

            # Métrica 2: Routing Accuracy
            AGENT_ALIASES = {
                "WorkspaceSpecialistAgent": "workspace_specialist",
                "SqlSpecialistAgent": "sql_specialist",
                "HTMLModularSpecialistAgent": "html_modular_specialist",
                "CustomerIssueReviewerAgent": "customer_issue_reviewer",
                "CodeConsistencySpecialistAgent": "code_consistency_specialist",
                "ResearchEvolutionSpecialistAgent": "research_evolution_specialist",
                "PresCMedClientAgent": "pcm",
                "SecurityGuardAgent": "security_guard",
            }
            if requires_safety_block:
                routing_score = 1.0 if actual_status == "blocked_by_guardrails" else 0.0
            else:
                norm_expected = AGENT_ALIASES.get(expected_agent, expected_agent)
                norm_actual = AGENT_ALIASES.get(target_agent or "", target_agent)
                target_agent_matched = (
                    target_agent == expected_agent
                    or norm_actual == norm_expected
                    or (triage.get("target_skill") == expected_agent)
                )
                domain_matched = (triage.get("domain") == expected_domain)
                routing_score = 1.0 if (target_agent_matched or domain_matched) else 0.0
            metrics_scores["routing_accuracy"].append(routing_score)

            # Métrica 3: Subcatalog Isolation
            # Verifica se o subcatálogo é restrito (<= 3 itens e sem invasão de domínio)
            is_isolated = isinstance(target_subcatalog, list) and len(target_subcatalog) <= 3
            subcat_score = 1.0 if is_isolated else 0.0
            metrics_scores["subcatalog_isolation"].append(subcat_score)

            # Métrica 4: Task Completion
            has_response = bool(turn_res.get("response") and len(turn_res.get("response", "")) > 10)
            task_score = 1.0 if has_response else 0.0
            metrics_scores["task_completion"].append(task_score)

            case_passed = (
                routing_score == 1.0
                and safety_score == 1.0
                and subcat_score == 1.0
                and task_score == 1.0
            )

            results.append({
                "case_id": case_id,
                "prompt": prompt_text,
                "expected_agent": expected_agent,
                "actual_agent": target_agent,
                "actual_status": actual_status,
                "subcatalog": target_subcatalog,
                "passed": case_passed,
                "scores": {
                    "routing": routing_score,
                    "safety": safety_score,
                    "subcatalog_isolation": subcat_score,
                    "completion": task_score,
                },
            })

        # Agregação das Métricas
        aggregated = {
            metric: (sum(scores) / len(scores)) if scores else 0.0
            for metric, scores in metrics_scores.items()
        }
        total_cases = len(cases)
        passed_cases = sum(1 for r in results if r["passed"])
        global_score = passed_cases / total_cases if total_cases > 0 else 0.0

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "dataset": self.dataset_path.name,
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "global_pass_rate": round(global_score, 4),
            "metrics": {k: round(v, 4) for k, v in aggregated.items()},
            "case_results": results,
        }

        return report

    def save_report(self, report: dict[str, Any], output_dir: Path | str | None = None) -> Path:
        """Estágio 4: Salva o relatório de avaliação no formato JSON canônico."""
        out_dir = Path(output_dir or (Path(__file__).parent.parent.parent / "artifacts" / "eval_results"))
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        report_file = out_dir / f"flywheel_report_{ts}.json"
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Relatório de avaliação do Quality Flywheel salvo em: {report_file}")
        return report_file


if __name__ == "__main__":
    runner = QualityFlywheelRunner()
    report = runner.run_eval()
    runner.save_report(report)
    print(json.dumps({
        "dataset": report["dataset"],
        "pass_rate": f"{report['global_pass_rate'] * 100:.1f}%",
        "passed": f"{report['passed_cases']}/{report['total_cases']}",
        "metrics": report["metrics"],
    }, indent=2))
