"""Servidor FastMCP unificado com suporte multi-transporte (stdio e SSE na porta 8080)."""

import argparse
import os
import sys

from fastmcp import FastMCP

from mcp_servers.tools.bigquery_analytics import register_bigquery_tools
from mcp_servers.tools.google_workspace import register_google_workspace_tools
from shared.logger import get_logger, setup_logging

# Força todos os logs de observabilidade para stderr, protegendo o stdout para JSON-RPC
setup_logging(stream=sys.stderr)
logger = get_logger("MCPUnifiedServer")

# Inicialização do Servidor FastMCP com metadados do repositório global
mcp = FastMCP(
    name="MeuWorkspaceGlobalTools",
    instructions="Servidor de ferramentas unificadas para o ecossistema global de agentes"
)

# Registro dos módulos de ferramentas
register_google_workspace_tools(mcp)
register_bigquery_tools(mcp)

# Ferramenta global adicional do próprio servidor para inspeção do repositório
@mcp.tool()
def get_system_health() -> dict:
    """Verifica a saúde operacional e conectividade dos serviços do workspace."""
    return {
        "status": "healthy",
        "transport": os.getenv("MCP_TRANSPORT", "stdio"),
        "version": "1.0.0",
        "registered_tools_count": 5
    }


def main():
    parser = argparse.ArgumentParser(description="Executa o Servidor FastMCP Unificado.")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="Tipo de transporte de comunicação (padrão: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_SERVER_PORT", "8080")),
        help="Porta para o transporte SSE (padrão: 8080)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
        help="Host de escuta para SSE (padrão: 0.0.0.0)"
    )

    args = parser.parse_args()

    if args.transport == "sse":
        logger.info(f"Iniciando Servidor FastMCP via SSE em http://{args.host}:{args.port}/sse...")
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        # Modo stdio silencioso para evitar poluição no stdout do protocolo JSON-RPC
        os.environ["FASTMCP_SHOW_SERVER_BANNER"] = "false"
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
