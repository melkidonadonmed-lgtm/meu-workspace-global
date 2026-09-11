#!/usr/bin/env python3
"""Exemplo Canônico de Lifecycle Hooks no Google Antigravity SDK.

Localização: C:\\Users\\melki\\meu-workspace-global\\examples\\getting_started\\hooks.py

Demonstra como interceptar, observar e controlar eventos do ciclo de vida
do agente (sessão, turnos, chamadas de ferramentas e erros) utilizando
os decoradores @hooks da biblioteca google.antigravity.
"""

import asyncio
import sys
from typing import Any

try:
    from google.antigravity import Agent, LocalAgentConfig, types
    from google.antigravity.hooks import hooks
except ImportError:
    print(
        "Erro: Pacote 'google-antigravity' não encontrado. "
        "Instale via: pip install google-antigravity",
        file=sys.stderr,
    )
    sys.exit(1)


# ==============================================================================
# 1. Definição dos Hooks de Sessão
# ==============================================================================

@hooks.on_session_start
async def session_start_hook() -> None:
    """Disparado no momento em que a sessão do agente é inicializada."""
    print("🔵 [Hook] on_session_start: Sessão iniciada com sucesso.")


@hooks.on_session_end
async def session_end_hook() -> None:
    """Disparado quando a sessão do agente é finalizada."""
    print("🔴 [Hook] on_session_end: Sessão encerrada.")


# ==============================================================================
# 2. Definição dos Hooks de Turno (Turn Hooks)
# ==============================================================================

@hooks.pre_turn
async def pre_turn_hook(prompt: str) -> types.HookResult:
    """Disparado antes de processar um turno do usuário.
    
    Permite inspecionar o prompt, rejeitar ou aprovar a execução.
    """
    print(f"🟡 [Hook] pre_turn: Prompt recebido ('{prompt[:50]}...').")
    return types.HookResult(allow=True)


@hooks.post_turn
async def post_turn_hook(response_content: str) -> None:
    """Disparado após o término de um turno com a resposta final do modelo."""
    print(f"🟢 [Hook] post_turn: Resposta gerada ({len(response_content)} caracteres).")


# ==============================================================================
# 3. Definição dos Hooks de Ferramenta (Tool Hooks)
# ==============================================================================

@hooks.pre_tool_call_decide
async def pre_tool_decide_hook(tool_call: types.ToolCall) -> types.HookResult:
    """Disparado antes da execução de uma ferramenta para decidir aprovação ou bloqueio."""
    tool_name = tool_call.name
    print(f"🔍 [Hook] pre_tool_call_decide: Avaliando ferramenta '{tool_name}'...")

    if tool_name == "run_command":
        cmd = tool_call.args.get("CommandLine", "")
        if "rm " in cmd or "del " in cmd:
            print(f"⛔ [Hook] pre_tool_call_decide: Comando bloqueado pelo Guardrail: {cmd}")
            return types.HookResult(
                allow=False,
                message=f"Operação cancelada pelo guardrail de segurança: '{cmd}'.",
            )

    return types.HookResult(allow=True)


@hooks.post_tool_call
async def post_tool_hook(tool_result: Any) -> None:
    """Disparado após a execução bem-sucedida de uma ferramenta."""
    print("✅ [Hook] post_tool_call: Ferramenta executada com sucesso.")


@hooks.on_tool_error
async def tool_error_hook(error: Exception) -> None:
    """Disparado quando ocorre um erro na execução de uma ferramenta."""
    print(f"⚠️ [Hook] on_tool_error: Erro capturado na ferramenta: {error}")
    return None


# ==============================================================================
# 4. Configuração e Execução Principal
# ==============================================================================

async def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("DEMO: Lifecycle Hooks no Google Antigravity SDK")
    print("=" * 70)

    config = LocalAgentConfig(
        hooks=[
            session_start_hook,
            session_end_hook,
            pre_turn_hook,
            post_turn_hook,
            pre_tool_decide_hook,
            post_tool_hook,
            tool_error_hook,
        ]
    )

    prompt = "Explique em uma frase o que é o Model Context Protocol (MCP)."
    print(f"\n💬 Enviando mensagem para o agente: '{prompt}'\n")

    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        text = await response.text()
        print("\n" + "-" * 70)
        print(f"🤖 Resposta do Agente:\n{text}")
        print("-" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
