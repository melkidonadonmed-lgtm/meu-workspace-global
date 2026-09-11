#!/usr/bin/env python3
"""Exemplo Canônico de Integração MCP no Google Antigravity SDK.

Localização: C:\\Users\\melki\\meu-workspace-global\\examples\\getting_started\\mcp_tools.py
"""

import asyncio
import sys
from pathlib import Path

try:
    from google.antigravity import Agent, LocalAgentConfig, types
    from google.antigravity.hooks import policy
except ImportError:
    print(
        "Erro: Pacote 'google-antigravity' não encontrado. "
        "Instale via: pip install google-antigravity",
        file=sys.stderr,
    )
    sys.exit(1)


async def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("DEMO: Integração de Servidores MCP no Google Antigravity SDK")
    print("=" * 70)

    server_script = str(Path(__file__).parent / "sample_mcp_server.py")

    stdio_server = types.McpStdioServer(
        name="math_service",
        command=sys.executable,
        args=[server_script],
    )
    print(f"📦 Servidor Stdio configurado: '{stdio_server.name}'")

    remote_http_server = types.McpStreamableHttpServer(
        name="remote_service_example",
        url="https://api.example.com/mcp",
        headers={"Authorization": "Bearer sample-token-demonstrativo"},
    )
    print(f"🌐 Servidor Remoto Streamable HTTP mapeado: '{remote_http_server.name}'")

    policies = [
        policy.allow(stdio_server, ["add_numbers", "calculate_discount"]),
        policy.deny(stdio_server, ["restricted_admin_tool"]),
    ]
    print("🛡️ Políticas de segurança vinculadas ao servidor MCP configuradas com sucesso.\n")

    config = LocalAgentConfig(
        mcp_servers=[stdio_server],
        policies=policies,
    )

    prompt = (
        "Some os números 42 e 58 utilizando a ferramenta MCP 'add_numbers', "
        "e calcule quanto fica um produto de R$ 200,00 com 15% de desconto "
        "usando 'calculate_discount'. Responda em Português BR."
    )

    print(f"💬 Prompt enviado ao agente:\n\"{prompt}\"\n")

    try:
        async with Agent(config) as agent:
            response = await agent.chat(prompt)
            text = await response.text()
            print("-" * 70)
            print("🤖 Resposta do Agente com Ferramentas MCP:")
            print(text)
            print("-" * 70)
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
