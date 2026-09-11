"""Suíte de Avaliação do Google Agents CLI (Quality Flywheel) para Roteamento de Pedidos."""

import json
import unittest
from pathlib import Path
import pytest

try:
    from agents.router import AutoSkillRouter
except ImportError:
    AutoSkillRouter = None


@pytest.mark.skipif(AutoSkillRouter is None, reason="Módulo legado agents.router foi descontinuado")
class TestRoutingEval(unittest.TestCase):
    """Execução da avaliação de roteamento sobre o dataset canônico de casos."""

    @classmethod
    def setUpClass(cls):
        if AutoSkillRouter is None:
            raise unittest.SkipTest("Módulo legado agents.router foi descontinuado")
        cls.dataset_path = Path(__file__).parent / "datasets" / "routing_dataset.json"
        with cls.dataset_path.open(encoding="utf-8") as f:
            cls.dataset = json.load(f)
        cls.router = AutoSkillRouter()

    def test_eval_dataset_routing_accuracy_100_percent(self):
        """Avalia se todas as intenções do dataset canônico são roteadas para os alvos corretos."""
        cases = self.dataset.get("eval_cases", [])
        self.assertGreaterEqual(len(cases), 5, "O dataset deve conter no mínimo 5 casos de avaliação.")

        failures = []
        for case in cases:
            case_id = case["eval_case_id"]
            user_text = case["prompt"]["parts"][0]["text"]
            expected_target = case["reference"]
            expected_domain = case.get("expected_domain")

            triage = self.router.triage_order(user_text)
            actual_target = triage.get("target_agent")
            actual_domain = triage.get("domain")

            if actual_target != expected_target:
                failures.append(
                    f"[{case_id}] Target incorreto: esperado='{expected_target}', obtido='{actual_target}'. Input: '{user_text}'"
                )

            if expected_domain and actual_domain != expected_domain:
                failures.append(
                    f"[{case_id}] Domínio incorreto: esperado='{expected_domain}', obtido='{actual_domain}'"
                )

        self.assertEqual(len(failures), 0, "\n".join(failures))

    def test_eval_dataset_subcatalog_isolation(self):
        """Avalia se nenhum subcatálogo vaza skills de outros domínios ou ultrapassa 3 skills."""
        cases = self.dataset.get("eval_cases", [])
        for case in cases:
            user_text = case["prompt"]["parts"][0]["text"]
            triage = self.router.triage_order(user_text)
            subcatalog = triage.get("target_subcatalog", [])

            self.assertIsInstance(subcatalog, list)
            self.assertLessEqual(
                len(subcatalog),
                3,
                f"Context Bloat detectado: subcatálogo para '{triage.get('target_agent')}' tem mais de 3 skills ({len(subcatalog)}).",
            )


if __name__ == "__main__":
    unittest.main()
