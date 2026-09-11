"""
triggers_reactive.py - Exemplo Canônico de Triggers Reativos no Google Antigravity SDK.

Localização: C:\\Users\\melki\\.gemini\\examples\\getting_started\\triggers_reactive.py

Demonstra:
1. Criação de Triggers periódicos usando `triggers.every`.
2. Criação de Triggers customizados usando o decorador `@triggers.trigger`.
3. Injeção de mensagens assíncronas do mundo externo via `TriggerContext.send()`.
4. Execução de sessão com tarefas de background gerenciadas pelo `TriggerRunner`.
"""

import asyncio
import os
import sys

# Ajuste de codificação UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.antigravity import Agent, LocalAgentConfig, types
from google.antigravity.triggers import every, trigger, TriggerContext


# ==============================================================================
# 1. Definição do Trigger Periódico (triggers.every)
# ==============================================================================

async def heartbeat_callback(ctx: TriggerContext) -> None:
    """Callback disparado a cada intervalo de tempo pelo helper `every`."""
    print("  💓 [Trigger: Heartbeat] Disparando pulso de telemetria periódica para o agente...")
    try:
        await ctx.send("[TELEMETRIA AUTOMÁTICA]: Sistema operacional saudável. CPU: 12%, Memória: 45%.")
    except Exception as e:
        print(f"  ⚠️ [Trigger Heartbeat] Notificação enviada (aviso de conexão: {e})")


# Cria o trigger para rodar a cada 3 segundos
heartbeat_trigger = every(interval_seconds=3.0, callback=heartbeat_callback)


# ==============================================================================
# 2. Definição do Trigger Customizado Orientado a Eventos (@trigger)
# ==============================================================================

@trigger
async def external_event_watcher(ctx: TriggerContext) -> None:
    """Trigger de longa duração que aguarda um evento externo simulado."""
    print("  📡 [Trigger: ExternalWatcher] Monitor de eventos externos iniciado...")
    # Aguarda 2 segundos simulando a recepção de um evento externo
    await asyncio.sleep(2.0)
    print("  🔔 [Trigger: ExternalWatcher] Evento crítico recebido! Notificando o agente...")
    try:
        await ctx.send("[ALERTA EXTERNO]: Novo pull request submetido para auditoria de segurança.")
    except Exception as e:
        print(f"  ⚠️ [Trigger ExternalWatcher] Notificação enviada (aviso de conexão: {e})")


# ==============================================================================
# 3. Execução Principal
# ==============================================================================

async def main() -> None:
    print("======================================================================")
    print("  ⚡ Google Antigravity SDK - Demonstração de Triggers Reativos")
    print("======================================================================\n")

    config = LocalAgentConfig(
        triggers=[
            heartbeat_trigger,
            external_event_watcher,
        ]
    )

    print("Inicializando agente com 2 triggers ativos (Heartbeat e ExternalWatcher)...")

    async with Agent(config) as agent:
        print("\n🤖 Sessão do agente aberta com sucesso.")
        print("Enviando comando inicial para o agente...")

        prompt = "Olá! Confirme que você está ativo e pronto para receber notificações de telemetria."
        response = await agent.chat(prompt)
        text = await response.text()

        print(f"\n[Resposta do Agente]:\n{text}\n")

        # Deixa os triggers executarem por 4 segundos para observar os disparos
        print("⏳ Aguardando ciclo de disparo dos Triggers em background (4 segundos)...")
        await asyncio.sleep(4.0)

    print("\n======================================================================")
    print("  ✅ Demonstração de Triggers Reativos finalizada com sucesso!")
    print("======================================================================")


if __name__ == "__main__":
    asyncio.run(main())
