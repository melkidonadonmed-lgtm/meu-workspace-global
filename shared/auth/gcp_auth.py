"""Gerenciamento de credenciais do Google Cloud (GCP) com fallback resiliente."""

import os
from typing import Any

from shared.logger import get_logger

logger = get_logger("GCPAuth")

DEFAULT_GCP_PROJECT_ID = "agent-md-506215"


def get_gcp_project_id() -> str:
    """Retorna o ID do projeto Google Cloud configurado no ambiente."""
    return os.getenv("GCP_PROJECT_ID", DEFAULT_GCP_PROJECT_ID)


def get_gcp_credentials(scopes: list[str] | None = None) -> tuple[Any, str]:
    """Obtém credenciais do Google Cloud via Application Default Credentials (ADC) ou Service Account.

    Retorna uma tupla (credentials, project_id). Se não houver credenciais configuradas,
    retorna (None, project_id) para acionar o modo de simulação/fallback seguro.
    """
    project_id = get_gcp_project_id()
    try:
        import google.auth

        credentials, detected_project = google.auth.default(scopes=scopes)
        resolved_project = project_id or detected_project or DEFAULT_GCP_PROJECT_ID
        logger.info(f"Credenciais GCP obtidas com sucesso para o projeto: {resolved_project}")
        return credentials, resolved_project
    except Exception as e:  # noqa: BLE001 - fallback proposital para ambientes sem gcloud auth
        logger.warning(
            f"Credenciais GCP não encontradas ou inválidas ({e}). "
            f"Operando em modo seguro/simulado para o projeto {project_id}."
        )
        return None, project_id
