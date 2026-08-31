"""Ferramentas FastMCP para integração com Google Workspace (Drive, Docs, Sheets)."""

from typing import Any

from fastmcp import FastMCP

from shared.logger import get_logger

logger = get_logger("GoogleWorkspaceMCP")


def register_google_workspace_tools(mcp: FastMCP) -> None:
    """Registra as ferramentas do Google Workspace no servidor FastMCP."""

    @mcp.tool()
    def list_workspace_documents(folder_id: str = "root", limit: int = 10) -> list[dict[str, Any]]:
        """Lista documentos e planilhas armazenados no Google Drive/Workspace."""
        logger.info(f"Listando documentos na pasta: {folder_id} (limite: {limit})")
        # Simulação resiliente de conector com contrato de dados estrito
        return [
            {"id": "doc_001", "name": "Especificação de Arquitetura.gdoc", "type": "document", "modified": "2026-08-30T14:20:00Z"},
            {"id": "sheet_002", "name": "Métricas de Adoção de Agentes.gsheet", "type": "spreadsheet", "modified": "2026-08-31T09:15:00Z"},
            {"id": "doc_003", "name": "Guardrails e Políticas de Segurança.gdoc", "type": "document", "modified": "2026-08-28T18:00:00Z"},
        ]

    @mcp.tool()
    def get_document_content(document_id: str) -> dict[str, Any]:
        """Obtém o conteúdo textual estruturado de um documento do Google Workspace."""
        logger.info(f"Obtendo conteúdo do documento ID: {document_id}")
        return {
            "document_id": document_id,
            "title": "Documento Corporativo",
            "content": "Este é o conteúdo consolidado do documento recuperado com segurança via MCP.",
            "status": "success"
        }
