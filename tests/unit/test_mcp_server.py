"""Smoke tests do Servidor FastMCP unificado e suas tools registradas."""

from mcp_servers.server import mcp

EXPECTED_TOOLS = {
    "login_google_workspace",
    "get_workspace_auth_status",
    "list_workspace_documents",
    "get_document_content",
    "list_upcoming_calendar_events",
    "list_storage_files",
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


async def test_calendar_and_storage_tools():
    """Garante a execução resiliente das ferramentas de Calendar e Cloud Storage."""
    cal_tool = await mcp.get_tool("list_upcoming_calendar_events")
    cal_result = cal_tool.fn(max_results=3)
    assert isinstance(cal_result, list)
    assert len(cal_result) > 0

    storage_tool = await mcp.get_tool("list_storage_files")
    storage_result = storage_tool.fn(bucket_name="agent-md-506215-backups", max_results=2)
    assert isinstance(storage_result, list)
    assert len(storage_result) > 0


async def test_workspace_auth_status_tool():
    """Verifica que a ferramenta de status de autenticação retorna diagnóstico estruturado."""
    status_tool = await mcp.get_tool("get_workspace_auth_status")
    result = status_tool.fn()
    assert isinstance(result, dict)
    assert "status" in result
    assert "authenticated" in result

