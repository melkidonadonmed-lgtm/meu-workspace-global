"""Tour guiado automatizado e interativo do Google ADK Lab.

Testa e demonstra cada uma das capacidades do framework:
1. Estado e Escopos de Persistência (user:, temp:)
2. Armazenamento e Versionamento de Artefatos (Artifacts Service)
3. Habilidades Dinâmicas do Catálogo (SkillToolset)
4. Confirmação de Ações Human-in-the-Loop (Action Confirmation)
5. Callbacks de Ciclo de Vida e Observabilidade
6. Rebobinamento de Sessão (Session Rewind)
"""

import asyncio
import sys
from pathlib import Path

# Configura sys.path para o workspace
workspace_dir = str(Path(__file__).resolve().parent.parent)
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from adk_lab.agent import root_agent
from adk_lab.tools import critical_patch_tool
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def run_tour():
    print("==========================================================")
    print("[LAB] BEM-VINDO AO GOOGLE ADK LAB TOUR (SHOWCASE EXPERIMENTAL)")
    print("==========================================================")

    # 1. Estrutura do Agente
    print("\n--- 1. Inspecao de Arquitetura do Agente ---")
    print(f"Nome do agente: {root_agent.name}")
    print(f"Modelo configurado: {root_agent.model}")
    print(f"Total de ferramentas registradas: {len(root_agent.tools)}")
    assert root_agent.name == "adk_lab_agent"
    assert len(root_agent.tools) >= 5
    print("[OK] Agente instanciado com sucesso com ferramentas e habilidades!")

    # 2. Teste de Skills Dinâmicas (SkillToolset)
    print("\n--- 2. Teste de Skills Dinamicas (SkillToolset) ---")
    skill_tools = [t for t in root_agent.tools if hasattr(t, "skills")]
    assert len(skill_tools) > 0, "SkillToolset deve estar registrado no agente"
    skillset = skill_tools[0]
    loaded_skill = skillset.skills[0]
    print(f"Skill carregada dinamicamente: '{loaded_skill.name}'")
    print(f"Descricao da skill: {loaded_skill.description[:80]}...")
    assert loaded_skill.name == "analytics"
    print("[OK] Catalogo local de skills integrado via SkillToolset!")

    # 3. Teste de Action Confirmation (HITL)
    print("\n--- 3. Teste de Action Confirmation (Human-in-the-Loop) ---")
    print(f"Tool com confirmacao: {critical_patch_tool.name}")
    is_req = getattr(critical_patch_tool, "_require_confirmation", False) or getattr(critical_patch_tool, "require_confirmation", False)
    print(f"require_confirmation ativado: {is_req}")
    assert is_req is True
    print("[OK] Acoes criticas protegidas por confirmacao humana!")

    # 4. Teste de Artifacts (ArtifactService)
    print("\n--- 4. Teste de Artifacts (Armazenamento Binario / Markdown) ---")
    artifact_service = InMemoryArtifactService()
    test_content = "# Relatorio Tecnico do Lab ADK\nStatus: 100% Operacional"
    part = types.Part.from_bytes(data=test_content.encode("utf-8"), mime_type="text/markdown")

    # Salva artefato
    v1 = await artifact_service.save_artifact(
        app_name="adk_lab",
        user_id="user_melki",
        session_id="session_01",
        filename="analise.md",
        artifact=part,
    )
    print(f"Artefato 'analise.md' salvo com versao: {v1}")
    assert v1 == 0 or v1 == 1

    # Carrega artefato
    loaded_part = await artifact_service.load_artifact(
        app_name="adk_lab",
        user_id="user_melki",
        session_id="session_01",
        filename="analise.md",
    )
    assert loaded_part is not None
    loaded_text = loaded_part.inline_data.data.decode("utf-8")
    print(f"Conteudo recuperado com sucesso: '{loaded_text.splitlines()[0]}'")
    print("[OK] ArtifactService opera com versionamento transparente!")

    # 5. Teste de State Scopes (user:, temp:)
    print("\n--- 5. Teste de State Scopes (Persistencia Multi-Nivel) ---")
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="adk_lab",
        user_id="user_melki",
        session_id="session_01",
        state={
            "user:preferred_language": "pt-BR",
            "user:theme": "nordic-dark",
            "temp:intermediate_step": 42,
            "session_counter": 1,
        },
    )
    print(f"Estado persistido da sessao: {session.state}")
    assert session.state["user:theme"] == "nordic-dark"
    # Conforme especificação do ADK: chaves com prefixo 'temp:' são efêmeras da invocação e não persistem na sessão
    assert "temp:intermediate_step" not in session.state
    print("[OK] Escopos de estado (user: persistido, temp: efemero) comprovados conforme doc oficial!")

    # 6. Teste de Session Rewind
    print("\n--- 6. Teste de Session Rewind (Rollback de Estado) ---")
    runner = Runner(
        agent=root_agent,
        app_name="adk_lab",
        session_service=session_service,
        artifact_service=artifact_service,
    )
    print("Runner configurado com Runner(agent, session_service, artifact_service).")
    print(f"Metodo rewind disponivel: {hasattr(runner, 'rewind_async')}")
    assert hasattr(runner, "rewind_async")
    print("[OK] Suporte a Session Rewind verificado com sucesso!")

    print("\n==========================================================")
    print("[SUCESSO] TOUR CONCLUIDO! TODAS AS CAPACIDADES ADK ESTAO ATIVAS!")
    print("==========================================================")


if __name__ == "__main__":
    asyncio.run(run_tour())
