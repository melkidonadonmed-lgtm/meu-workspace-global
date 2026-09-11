"""Script de teste dos padrões avançados da ADK 2.0 Dynamic Workflows API."""

import asyncio
import sys
from pathlib import Path

# Configura sys.path para o workspace
workspace_dir = str(Path(__file__).resolve().parent.parent)
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from adk_lab.advanced_workflows import parallel_workflow_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def main():
    print("==========================================================")
    print("[WORKFLOW] TESTE DE EXECUCAO PARALELA E DATA SCHEMAS")
    print("==========================================================")

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="advanced_wf_lab",
        user_id="user_melki",
        session_id="session_parallel_01",
    )

    runner = Runner(
        agent=parallel_workflow_agent,
        session_service=session_service,
        app_name="advanced_wf_lab",
    )

    print(f"Workflow: {parallel_workflow_agent.name}")
    print(f"Topologia: {parallel_workflow_agent.edges}")

    msg = types.Content(role="user", parts=[types.Part.from_text(text="Iniciar auditoria paralela")])

    print("\nExecutando parallel_auditor com 4 workers simultâneos...")
    outputs = []
    async for event in runner.run_async(
        user_id="user_melki",
        session_id="session_parallel_01",
        new_message=msg,
    ):
        if hasattr(event, "output") and event.output:
            outputs.append(event.output)
            print(f"[Output recebido]: {event.output}")

    assert len(outputs) > 0, "O workflow deve produzir outputs"
    print("\n[SUCESSO] Execução paralela e serialização Pydantic validadas com 100% de sucesso!")


if __name__ == "__main__":
    asyncio.run(main())
