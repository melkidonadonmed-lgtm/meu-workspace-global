"""Script de execução e validação da ADK 2.0 Graph Workflow API."""

import asyncio
import sys
from pathlib import Path

# Configura sys.path para o workspace
workspace_dir = str(Path(__file__).resolve().parent.parent)
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from adk_lab.workflow_demo import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def main():
    print("==========================================================")
    print("[WORKFLOW] TESTE DA GOOGLE ADK 2.0 GRAPH WORKFLOW API")
    print("==========================================================")

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="workflow_demo",
        user_id="user_melki",
        session_id="wf_session_01",
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="workflow_demo",
    )

    print(f"Nome do Workflow: {root_agent.name}")
    print(f"Topologia de arestas (edges): {root_agent.edges}")

    user_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Disparar workflow!")],
    )

    print("\nExecutando o fluxo de nós (START -> my_workflow -> hello_node)...")
    outputs = []
    async for event in runner.run_async(
        user_id="user_melki",
        session_id="wf_session_01",
        new_message=user_msg,
    ):
        if hasattr(event, "output") and event.output:
            outputs.append(event.output)
            print(f"[Evento de Saída do Nó]: {event.output}")

    assert len(outputs) > 0, "O workflow deve produzir saídas dos nós"
    print("\n[SUCESSO] Workflow executado e validado com 100% de sucesso!")


if __name__ == "__main__":
    asyncio.run(main())
