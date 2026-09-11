"""
human_in_the_loop.py - Exemplo Canônico de Human-in-the-Loop (HITL) no Google Antigravity SDK.

Localização: C:\\Users\\melki\\.gemini\\examples\\getting_started\\human_in_the_loop.py

Demonstra:
1. Políticas declarativas de confirmação humana via `policy.ask_user` e `policy.confirm_run_command`.
2. Implementação de manipuladores `AskUserHandler` para decisão interativa do operador humano.
3. Ganchos de decisão finos `@hooks.pre_tool_call_decide` para autorizar, rejeitar ou sanitizar/modificar argumentos em tempo real.
4. Resolução de perguntas do agente ao usuário via `@hooks.on_interaction`.
5. Suporte a modo demonstrativo automático e modo interativo via flag `--interactive`.
"""

import argparse
import asyncio
import os
import sys
from typing import Any

# Garantir UTF-8 no Windows para manipulação correta de acentuação
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.antigravity import Agent, LocalAgentConfig, types
from google.antigravity.hooks import hooks, policy

# ==============================================================================
# 1. Ferramentas de Teste do Domínio (Tools)
# ==============================================================================

def execute_system_maintenance(action: str, target: str) -> str:
    """Executa ações administrativas ou manutenção no sistema.
    
    Args:
        action: Ação a ser executada (ex: 'backup', 'optimize', 'purge').
        target: Alvo da ação (ex: 'production_db', 'staging_db', 'logs').
    """
    print(f"  ⚡ [Tool: execute_system_maintenance] Executando '{action}' no alvo '{target}'...")
    return f"Manutenção '{action}' executada com sucesso no alvo '{target}'."


def deploy_service(environment: str, version: str) -> str:
    """Realiza o deploy de um serviço de software.
    
    Args:
        environment: Ambiente de destino ('production', 'staging', 'dev').
        version: Versão do artefato (ex: 'v1.4.0').
    """
    print(f"  🚀 [Tool: deploy_service] Publicando versão {version} no ambiente [{environment}]...")
    return f"Deploy da versão {version} finalizado no ambiente {environment}."


# ==============================================================================
# 2. Manipulador de HITL via Política Declarativa (AskUserHandler)
# ==============================================================================

class HitlController:
    """Controlador que orquestra as decisões do operador humano."""

    def __init__(self, interactive: bool = False, auto_approve: bool = True):
        self.interactive = interactive
        self.auto_approve = auto_approve

    async def handle_ask_user(self, tool_call: types.ToolCall) -> bool:
        """Manipulador invocado pela política `policy.ask_user` quando uma ferramenta sensível é chamada."""
        print(f"\n🛑 [HITL Gatekeeper] O agente solicitou autorização para a ferramenta: '{tool_call.name}'")
        print(f"   Parâmetros solicitados: {tool_call.args}")

        if self.interactive:
            choice = input("   👉 Deseja autorizar a execução desta ação? (s/n): ").strip().lower()
            authorized = choice in ("s", "sim", "y", "yes")
        else:
            # Em modo não interativo / simulação controlada
            authorized = self.auto_approve
            print(f"   [Modo Demonstração] Decisão automatizada: {'AUTORIZADO' if authorized else 'REJEITADO'}")

        if authorized:
            print("   ✅ Operador humano aprovou a chamada da ferramenta.")
        else:
            print("   ⛔ Operador humano rejeitou a chamada da ferramenta.")
        return authorized


# ==============================================================================
# 3. Hook Fino de Decisão e Modificação de Argumentos
# ==============================================================================

@hooks.pre_tool_call_decide
async def fine_grained_hitl_decide(tool_call: types.ToolCall) -> types.HookResult:
    """Hook que inspeciona a chamada e pode sanitizar ou alterar argumentos antes da execução."""
    tool_name = tool_call.name

    # Exemplo: Se o agente tentar executar deploy em ambiente 'production',
    # o operador humano intercepta e redireciona com segurança para 'staging_sandbox'
    if tool_name == "deploy_service":
        env = tool_call.args.get("environment", "")
        if env.lower() == "production":
            print("\n🛡️ [Guardrail / HITL Sanitizer] Tentativa de deploy direto em 'production' detectada!")
            print("   Redirecionando parâmetros para 'staging_sandbox' por política de segurança Zero-Trust...")
            
            # Cria cópia sanitizada dos argumentos
            new_args = dict(tool_call.args)
            new_args["environment"] = "staging_sandbox"
            
            return types.HookResult(
                allow=True,
                modified_args=new_args,
            )

    # Para todas as outras chamadas, permite a execução normal
    return types.HookResult(allow=True)


# ==============================================================================
# 4. Hook de Interação e Resolução de Perguntas (OnInteractionHook)
# ==============================================================================

@hooks.on_interaction
async def hitl_interaction_handler(spec: types.AskQuestionInteractionSpec) -> types.QuestionHookResult:
    """Intercepta interações de perguntas estruturadas quando o agente precisa de clarificação."""
    print(f"\n❓ [HITL Interaction] O agente enviou {len(spec.questions)} pergunta(s) de clarificação:")
    responses: list[types.QuestionResponse] = []

    for i, q in enumerate(spec.questions, start=1):
        print(f"   [{i}] Pergunta: {q.question}")
        if q.options:
            print("       Opções disponíveis:")
            for opt in q.options:
                print(f"         - ({opt.id}): {opt.text}")

        # Resposta automática para demonstração não interativa
        first_option = [q.options[0].id] if q.options else None
        responses.append(
            types.QuestionResponse(
                selected_option_ids=first_option,
                freeform_response="Decisão tomada pelo operador humano via política HITL.",
            )
        )

    return types.QuestionHookResult(responses=responses)


# ==============================================================================
# 5. Execução dos Cenários Demonstrativos
# ==============================================================================

async def run_scenario_approval(controller: HitlController) -> None:
    """Cenário 1: Operador aprova chamada de ferramenta sensível."""
    print("\n" + "=" * 70)
    print("  Cenário 1: Aprovação Humana de Operação de Manutenção (policy.ask_user)")
    print("=" * 70)

    # Configura a política exigindo confirmação humana para 'execute_system_maintenance'
    hitl_policies = [
        policy.ask_user("execute_system_maintenance", handler=controller.handle_ask_user),
        policy.confirm_run_command(handler=controller.handle_ask_user),
    ]

    config = LocalAgentConfig(
        tools=[execute_system_maintenance, deploy_service],
        policies=hitl_policies,
        hooks=[fine_grained_hitl_decide, hitl_interaction_handler],
    )

    async with Agent(config) as agent:
        prompt = (
            "Por favor, execute a manutenção 'optimize' no banco de dados 'staging_db' "
            "usando a ferramenta apropriada."
        )
        print(f"Prompt do Usuário: '{prompt}'")
        response = await agent.chat(prompt)
        text = await response.text()
        print(f"\n🤖 Resposta Final do Agente:\n{text}")


async def run_scenario_sanitization() -> None:
    """Cenário 2: Modificação/Sanitização de Parâmetros pelo Guardrail HITL."""
    print("\n" + "=" * 70)
    print("  Cenário 2: Sanitização de Parâmetros em Tempo Real (modified_args)")
    print("=" * 70)

    config = LocalAgentConfig(
        tools=[execute_system_maintenance, deploy_service],
        hooks=[fine_grained_hitl_decide],
    )

    async with Agent(config) as agent:
        prompt = "Faça o deploy da versão v2.1.0 diretamente em 'production'."
        print(f"Prompt do Usuário: '{prompt}'")
        response = await agent.chat(prompt)
        text = await response.text()
        print(f"\n🤖 Resposta Final do Agente:\n{text}")


async def run_scenario_rejection(controller: HitlController) -> None:
    """Cenário 3: Operador humano rejeita a operação e o agente lida com o bloqueio."""
    print("\n" + "=" * 70)
    print("  Cenário 3: Rejeição da Ferramenta pelo Operador Humano")
    print("=" * 70)

    # Força a rejeição neste cenário
    controller.auto_approve = False

    hitl_policies = [
        policy.ask_user("execute_system_maintenance", handler=controller.handle_ask_user),
    ]

    config = LocalAgentConfig(
        tools=[execute_system_maintenance],
        policies=hitl_policies,
    )

    async with Agent(config) as agent:
        prompt = "Execute a manutenção 'purge' na tabela 'production_db' agora mesmo."
        print(f"Prompt do Usuário: '{prompt}'")
        response = await agent.chat(prompt)
        text = await response.text()
        print(f"\n🤖 Resposta Adaptativa do Agente:\n{text}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Google Antigravity SDK - Human-in-the-Loop Demo")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Habilita confirmação interativa do operador humano via terminal stdin.",
    )
    args = parser.parse_args()

    controller = HitlController(interactive=args.interactive, auto_approve=True)

    print("======================================================================")
    print("  🛡️ Google Antigravity SDK - Demonstração de Human-in-the-Loop (HITL)")
    print("======================================================================")

    # Executa os 3 cenários de demonstração
    await run_scenario_approval(controller)
    await run_scenario_sanitization()
    await run_scenario_rejection(controller)

    print("\n======================================================================")
    print("  ✅ Todos os cenários de Human-in-the-Loop foram demonstrados com sucesso!")
    print("======================================================================")


if __name__ == "__main__":
    asyncio.run(main())
