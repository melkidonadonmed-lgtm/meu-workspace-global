#!/usr/bin/env python3
"""Exemplo Canônico de Configuração de Persona no Google Antigravity SDK.

Localização: C:\\Users\\melki\\meu-workspace-global\\examples\\getting_started\\persona_config.py
"""

import asyncio
import sys

try:
    from google.antigravity import Agent, LocalAgentConfig
    from google.antigravity.types import CustomSystemInstructions, TemplatedSystemInstructions
except ImportError:
    print(
        "Erro: Pacote 'google-antigravity' não encontrado. "
        "Instale via: pip install google-antigravity",
        file=sys.stderr,
    )
    sys.exit(1)


async def demo_templated_instructions() -> None:
    print("\n" + "=" * 70)
    print("1. DEMO: TemplatedSystemInstructions (Identidade Especialista)")
    print("=" * 70)

    identity = (
        "Você é um arquiteto de software sênior do ecossistema Antigravity, "
        "com comunicação técnica impecável, direta e estritamente em Português BR."
    )

    templated_si = TemplatedSystemInstructions(identity=identity)
    config = LocalAgentConfig(system_instructions=templated_si)

    async with Agent(config) as agent:
        prompt = "Apresente-se em uma frase destacando sua especialidade."
        print(f"💬 Pergunta: '{prompt}'")
        response = await agent.chat(prompt)
        print(f"🤖 Resposta:\n{await response.text()}\n")


async def demo_shorthand_instructions() -> None:
    print("=" * 70)
    print("2. DEMO: Shorthand com String Simples (Instrução Complementar)")
    print("=" * 70)

    config = LocalAgentConfig(
        system_instructions="Sempre responda utilizando bullet points estruturados e emojis temáticos."
    )

    async with Agent(config) as agent:
        prompt = "Cite 3 benefícios do protocolo MCP."
        print(f"💬 Pergunta: '{prompt}'")
        response = await agent.chat(prompt)
        print(f"🤖 Resposta:\n{await response.text()}\n")


async def demo_custom_instructions() -> None:
    print("=" * 70)
    print("3. DEMO: CustomSystemInstructions (Sobrescrita Total e Estrita)")
    print("=" * 70)

    custom_si = CustomSystemInstructions(
        text="Você é um validador binário de conformidade. Responda exclusivamente com 'CONFORME' ou 'NÃO CONFORME'."
    )
    config = LocalAgentConfig(system_instructions=custom_si)

    async with Agent(config) as agent:
        prompt = "O código possui cobertura de testes de 100% e tipagem estrita?"
        print(f"💬 Pergunta: '{prompt}'")
        response = await agent.chat(prompt)
        print(f"🤖 Resposta: {await response.text().strip()}\n")


async def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("🚀 Iniciando demonstração de Personas no Google Antigravity SDK...")
    await demo_templated_instructions()
    await demo_shorthand_instructions()
    await demo_custom_instructions()
    print("✅ Todas as demonstrações de persona foram executadas com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())
