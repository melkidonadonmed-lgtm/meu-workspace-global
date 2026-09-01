"""Módulo de autenticação compartilhada para Google Cloud e Google Workspace."""

from shared.auth.gcp_auth import get_gcp_credentials, get_gcp_project_id
from shared.auth.workspace_auth import get_workspace_credentials

__all__ = ["get_gcp_credentials", "get_gcp_project_id", "get_workspace_credentials"]
