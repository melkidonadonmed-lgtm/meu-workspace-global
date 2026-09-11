"""Definição do root_agent para o audit_agent (Google ADK 2.9).

Combina ferramentas determinísticas de resolução de projetos e análise de código
com callbacks de segurança em tempo de execução (Zero-Trust).
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent

from .callbacks import after_model_guard, before_model_guard, before_tool_guard
from .tools import (
    check_code_drift,
    inspect_code_contracts,
    list_available_projects,
    scan_project_structure,
)

# Carrega variáveis de ambiente
load_dotenv()

# =====================================================================
# 🤖 Instanciação do Root Agent do ADK
# =====================================================================

root_agent = Agent(
    name="audit_agent",
    model=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
    instruction=(
        "Você é o Agente Especialista em Auditoria de Código, Arquitetura e Resolução de Projetos "
        "do ecossistema global de Melki. Suas diretrizes operacionais mandatórias são:\n"
        "1. Segurança Zero-Trust: Opere estritamente dentro dos projetos clientes autorizados (projects/*). "
        "Nunca tente auditar a pasta de agentes ou a raiz do meta-workspace.\n"
        "2. Resolução Precisa: Sempre utilize a ferramenta 'scan_project_structure' para mapear stacks, "
        "dependências e árvores de diretórios a partir dos aliases oficiais (pcm, canvas_ide, WAOE, keepdocs).\n"
        "3. Análise Estática: Utilize 'inspect_code_contracts' e 'check_code_drift' para validar assinaturas "
        "e garantir conformidade arquitetural.\n"
        "4. Comunicação: Responda sempre em Português BR com precisão técnica e clareza."
    ),
    description=(
        "Agente inteligente do Google ADK para auditoria de repositórios, resolução determinística "
        "de projetos e garantia de padrões de consistência de código."
    ),
    tools=[
        list_available_projects,
        scan_project_structure,
        inspect_code_contracts,
        check_code_drift,
    ],
    before_model_callback=before_model_guard,
    before_tool_callback=before_tool_guard,
    after_model_callback=after_model_guard,
)
