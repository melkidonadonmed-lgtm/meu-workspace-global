"""Módulo de ferramentas MCP para conectores externos e utilitários."""

from mcp_servers.tools.bigquery_analytics import register_bigquery_tools
from mcp_servers.tools.google_workspace import register_google_workspace_tools

__all__ = ["register_bigquery_tools", "register_google_workspace_tools"]
