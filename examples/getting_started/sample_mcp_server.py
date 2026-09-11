#!/usr/bin/env python3
"""Servidor MCP de Demonstração (FastMCP / MCPServer).

Localização: C:\\Users\\melki\\meu-workspace-global\\examples\\getting_started\\sample_mcp_server.py
"""

import sys

try:
    from mcp.server.mcpserver import MCPServer
    server = MCPServer("SampleMathServer")
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
        server = FastMCP("SampleMathServer")
    except ImportError:
        print("Erro: Pacote 'mcp' não encontrado.", file=sys.stderr)
        sys.exit(1)


@server.tool()
def add_numbers(a: int, b: int) -> int:
    """Soma dois números inteiros."""
    return a + b


@server.tool()
def calculate_discount(price: float, percentage: float) -> float:
    """Calcula o preço final com desconto percentual."""
    discount = price * (percentage / 100.0)
    return round(price - discount, 2)


@server.tool()
def restricted_admin_tool(command: str) -> str:
    """Ferramenta administrativa sensível utilizada para demonstração de políticas de bloqueio."""
    return f"Operação administrativa '{command}' executada com sucesso."


if __name__ == "__main__":
    server.run()
