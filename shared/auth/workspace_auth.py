"""Gerenciamento de credenciais OAuth 2.0 para Google Workspace (Calendar, Gmail, Drive, Sheets)."""

import os
from typing import Any

from shared.logger import get_logger

logger = get_logger("WorkspaceAuth")

WORKSPACE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_workspace_credentials(scopes: list[str] | None = None) -> Any:
    """Obtém credenciais OAuth 2.0 permanentes via Refresh Token para a conta do usuário.

    Retorna um objeto google.oauth2.credentials.Credentials se as variáveis de ambiente
    estiverem presentes; caso contrário, retorna None para acionar o fallback seguro.
    """
    client_id = os.getenv("WORKSPACE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("WORKSPACE_OAUTH_CLIENT_SECRET")
    refresh_token = os.getenv("WORKSPACE_OAUTH_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        logger.debug(
            "Variáveis WORKSPACE_OAUTH_* incompletas no ambiente. "
            "Operando em modo seguro/simulado para Google Workspace."
        )
        return None

    try:
        from google.oauth2.credentials import Credentials

        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=scopes or WORKSPACE_SCOPES,
        )
        logger.info("Credenciais Google Workspace OAuth 2.0 inicializadas com sucesso.")
        return credentials
    except Exception as e:  # noqa: BLE001 - fallback proposital para falhas de inicialização
        logger.warning(f"Erro ao instanciar credenciais OAuth do Workspace: {e}")
        return None
