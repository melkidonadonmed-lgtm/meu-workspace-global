"""
hello_world.py - Exemplo Canônico de Introdução ao Google Antigravity SDK.

Demonstra:
1. Inicialização do LocalAgentConfig com suporte a thinking e streaming.
2. Chat básico assíncrono com extração de texto via `await response.text()`.
3. Streaming de tokens em tempo real com `async for token in response`.
4. Streaming do fluxo de pensamento (Chain-of-Thought) via `async for thought in response.thoughts`.
5. Modo interativo opcional com loop REPL através de `--interactive`.
"""

import argparse
import asyncio
import os
import sys

# Garantir UTF-8 no Windows para evitar problemas com caracteres acentuados
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.antigravity import Agent, LocalAgentConfig, types


async def demo_basic_chat(agent: Agent) -> None:
    """Executa um prompt simples e exibe a resposta textual completa."""
    prompt = "Em uma frase concisa, o que é o ecossistema Google Antigravity?"
    print(f"\n[1. Chat Básico] Enviando prompt: '{prompt}'")
    
    response = await agent.chat(prompt)
    text = await response.text()
    print("[Resposta Básica]:")
    print(f"  {text}\n")


async def demo_streaming_response(agent: Agent) -> None:
    """Demonstra o streaming de tokens em tempo real."""
    prompt = "Liste 3 pilares fundamentais da arquitetura de agentes modernos."
    print(f"[2. Streaming de Tokens] Enviando prompt: '{prompt}'")
    print("[Streaming]: ", end="", flush=True)

    response = await agent.chat(prompt)
    async for token in response:
        print(token, end="", flush=True)
    print("\n")


async def demo_streaming_thoughts(agent: Agent) -> None:
    """Demonstra a captura e streaming do raciocínio interno (Chain-of-Thought)."""
    prompt = "Resolva este enigma lógico: Se todos os A são B e nenhum B é C, o que podemos afirmar sobre A e C?"
    print(f"[3. Streaming de Pensamentos / CoT] Enviando prompt: '{prompt}'")

    response = await agent.chat(prompt)
    
    # Inspeciona pensamentos se suportado pelo modelo/configuração
    if hasattr(response, "thoughts"):
        print("[Pensamentos do Agente]:")
        async for thought in response.thoughts:
            print(f"  🤔 [Thinking]: {thought}", flush=True)
    else:
        print("  (Atributo 'thoughts' não disponível nesta resposta)")

    print("[Resposta Final]:")
    text = await response.text()
    print(f"  {text}\n")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Google Antigravity SDK - Hello World")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Inicia um loop interativo REPL com o agente.",
    )
    args = parser.parse_args()

    # Configuração do agente local
    config = LocalAgentConfig(
        capabilities=types.CapabilitiesConfig(
            enable_subagents=True,
            enable_streaming=True,
        )
    )

    print("========================================================")
    print("  🚀 Google Antigravity SDK - Getting Started Hello World")
    print("========================================================")

    async with Agent(config) as agent:
        if args.interactive:
            print("\nIniciando sessão interativa... (Digite 'exit' ou 'quit' para encerrar)")
            try:
                from google.antigravity.utils.interactive import run_interactive_loop
                await run_interactive_loop(agent)
            except (ImportError, AttributeError):
                # Fallback para loop interativo manual
                while True:
                    try:
                        user_query = input("\nVocê > ").strip()
                        if not user_query:
                            continue
                        if user_query.lower() in ("exit", "quit", ":q"):
                            print("Encerrando sessão interativa.")
                            break
                        resp = await agent.chat(user_query)
                        print("Agente > ", end="", flush=True)
                        async for token in resp:
                            print(token, end="", flush=True)
                        print()
                    except (KeyboardInterrupt, EOFError):
                        print("\nInterrompido pelo usuário.")
                        break
        else:
            # Demonstração padrão não interativa
            await demo_basic_chat(agent)
            await demo_streaming_response(agent)
            await demo_streaming_thoughts(agent)

    print("========================================================")
    print("  ✅ Demonstração do Hello World concluída com sucesso!")
    print("========================================================")


if __name__ == "__main__":
    asyncio.run(main())
