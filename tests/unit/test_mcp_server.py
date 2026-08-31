"""Smoke tests do Servidor FastMCP unificado e suas tools registradas."""

from mcp_servers.server import mcp

EXPECTED_TOOLS = {
    "list_workspace_documents",
    "get_document_content",
    "bigquery_execute_query",
    "bigquery_get_schema",
    "get_system_health",
}


async def test_mcp_server_registers_all_tools():
    """Garante que o servidor sobe e registra o conjunto esperado de ferramentas."""
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    assert EXPECTED_TOOLS.issubset(tool_names), (
        f"Ferramentas ausentes: {EXPECTED_TOOLS - tool_names}"
    )


async def test_bigquery_tool_blocks_destructive_query():
    """Garante o guardrail contra operações destrutivas no BigQuery."""
    tool = await mcp.get_tool("bigquery_execute_query")
    result = tool.fn(query="DROP TABLE analytics.agent_telemetry")
    assert result["status"] == "error"
    assert "bloqueadas" in result["error"]
