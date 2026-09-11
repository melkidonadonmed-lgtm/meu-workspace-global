"""Agente principal do laboratório de testes do Google ADK (adk_lab).

Configurado com suporte nativo a:
1. Artifacts (save/load de arquivos)
2. State Scopes (user:, temp:)
3. Action Confirmation (HITL com FunctionTool require_confirmation=True)
4. Skills dinâmicas (SkillToolset integrado ao catálogo local)
5. Callbacks de observabilidade em tempo de execução
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent

from .callbacks import (
    lab_after_model_callback,
    lab_after_tool_callback,
    lab_before_model_callback,
    lab_before_tool_callback,
)
from .tools import (
    build_skill_toolset_for_analytics,
    critical_patch_tool,
    generate_and_save_report,
    get_stored_report,
    get_user_preferences,
    set_user_preference,
)

# Carrega ambiente local ou herdado
load_dotenv()

# Instancia o conjunto de habilidades do catálogo local
analytics_skill_toolset = build_skill_toolset_for_analytics()

# =====================================================================
# 🤖 Instanciação do Root Agent do Laboratório ADK
# =====================================================================

root_agent = Agent(
    name="adk_lab_agent",
    model=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
    instruction=(
        "Você é o Agente do Laboratório Experimental do Google ADK (adk_lab_agent). "
        "Sua missão é testar e demonstrar todas as capacidades avançadas do framework:\n"
        "1. Artefatos: Salve e recupere relatórios markdown usando 'generate_and_save_report' e 'get_stored_report'.\n"
        "2. Gerenciamento de Estado: Persista preferências do usuário com 'set_user_preference' (prefixo 'user:').\n"
        "3. Ações Críticas com Confirmação Humana (HITL): Quando solicitado a aplicar patches de segurança, "
        "utilize 'apply_critical_system_patch' (que requer confirmação explícita do usuário).\n"
        "4. Skills: Utilize as orientações do catálogo de skills analíticas sempre que requisitado.\n"
        "Responda sempre com clareza técnica e precisão em Português BR."
    ),
    description="Agente de laboratório demonstrando Artifacts, State Scopes, HITL, Callbacks e Skills do ADK.",
    tools=[
        generate_and_save_report,
        get_stored_report,
        set_user_preference,
        get_user_preferences,
        critical_patch_tool,
        analytics_skill_toolset,
    ],
    before_tool_callback=lab_before_tool_callback,
    after_tool_callback=lab_after_tool_callback,
    before_model_callback=lab_before_model_callback,
    after_model_callback=lab_after_model_callback,
)
