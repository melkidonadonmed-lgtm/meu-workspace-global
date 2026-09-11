"""Teste automatizado de avaliação para o audit_agent (Google ADK Quality Flywheel)."""

import json
from pathlib import Path
from audit_agent.agent import root_agent
from audit_agent.callbacks import before_model_guard, before_tool_guard
from audit_agent.tools import list_available_projects, scan_project_structure
from google.adk.models.llm_request import LlmRequest
from google.genai import types


def test_adk_audit_dataset_eval():
    dataset_path = Path(__file__).parent / "datasets" / "adk_audit_dataset.json"
    assert dataset_path.exists(), f"Dataset não encontrado: {dataset_path}"

    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    cases = data.get("eval_cases", [])
    assert len(cases) == 4

    passed_count = 0

    for case in cases:
        case_id = case["eval_case_id"]
        prompt_text = case["prompt"]["parts"][0]["text"]
        ref_text = case["reference"]["response"]["parts"][0]["text"]

        # 1. Caso de listagem de projetos
        if case_id == "case_project_listing":
            res = list_available_projects()
            assert res["status"] == "success"
            assert res["count"] >= 4
            passed_count += 1

        # 2. Caso de scan do PCM
        elif case_id == "case_scan_pcm":
            scan_res = scan_project_structure("pcm", max_depth=2)
            assert scan_res["status"] == "success"
            assert "pcm" in scan_res["project_name"].lower()
            assert scan_res["port"] == 3000
            passed_count += 1

        # 3. Caso de injeção de prompt
        elif case_id == "case_prompt_injection_blocking":
            req = LlmRequest(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt_text)],
                    )
                ],
            )
            blocked_resp = before_model_guard(None, req)
            assert blocked_resp is not None
            assert "[BLOQUEIO DE SEGURANCA ZERO-TRUST]" in blocked_resp.content.parts[0].text
            passed_count += 1

        # 4. Caso de violação de fronteira
        elif case_id == "case_boundary_violation_blocking":
            blocked_tool = before_tool_guard(None, {"project_name_or_path": "skills/auditoria"}, None)
            assert blocked_tool is not None
            assert blocked_tool["code"] == "TARGET_PROHIBITED"
            passed_count += 1

    pass_rate = passed_count / len(cases)
    assert pass_rate == 1.0, f"Taxa de aprovação esperada 100%, obtida: {pass_rate * 100}%"
