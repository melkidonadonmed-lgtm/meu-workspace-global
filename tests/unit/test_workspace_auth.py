"""Testes unitários para o módulo de autenticação persistente do Google Workspace."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from shared.auth.workspace_auth import (
    WORKSPACE_SCOPES,
    get_client_secrets_path,
    get_token_storage_path,
    get_workspace_auth_info,
    get_workspace_credentials,
    save_credentials_to_file,
    update_env_file,
)


def test_client_secrets_path_found():
    """Garante que o arquivo de credenciais do cliente OAuth é localizado em configs/."""
    path = get_client_secrets_path()
    assert path is not None
    assert path.is_file()
    assert "credentials.json" in path.name or "oauth_client_desktop.json" in path.name


def test_token_storage_path_defined():
    """Valida que o caminho do token persistente aponta para configs/workspace_token.json."""
    token_path = get_token_storage_path()
    assert token_path.name == "workspace_token.json"
    assert token_path.parent.name == "configs"


def test_save_and_load_credentials(tmp_path: Path):
    """Verifica a serialização e carregamento de credenciais a partir de arquivo de token."""
    mock_creds = MagicMock()
    fake_data = {
        "token": "ya29.fake-token",
        "refresh_token": "1//fake-refresh-token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "scopes": WORKSPACE_SCOPES,
    }
    mock_creds.to_json.return_value = json.dumps(fake_data)

    test_token_file = tmp_path / "test_token.json"
    save_credentials_to_file(mock_creds, test_token_file)

    assert test_token_file.is_file()
    loaded_data = json.loads(test_token_file.read_text(encoding="utf-8"))
    assert loaded_data["token"] == "ya29.fake-token"
    assert loaded_data["refresh_token"] == "1//fake-refresh-token"


def test_get_workspace_credentials_from_file(tmp_path: Path):
    """Garante que get_workspace_credentials carrega corretamente o token gravado."""
    fake_token_file = tmp_path / "workspace_token.json"
    fake_token_file.write_text("{}", encoding="utf-8")

    mock_credentials = MagicMock()
    mock_credentials.expired = False
    mock_credentials.valid = True

    with patch("shared.auth.workspace_auth.get_token_storage_path", return_value=fake_token_file), \
         patch("google.oauth2.credentials.Credentials.from_authorized_user_file", return_value=mock_credentials):
        creds = get_workspace_credentials()
        assert creds is not None
        assert creds.valid is True


def test_get_workspace_auth_info_unauthenticated():
    """Valida a estrutura de diagnóstico quando não há credenciais persistidas ou no ambiente."""
    with patch("shared.auth.workspace_auth.get_token_storage_path", return_value=Path("non_existent_token.json")), \
         patch("shared.auth.workspace_auth.get_workspace_credentials", return_value=None):
        info = get_workspace_auth_info()
        assert info["authenticated"] is False
        assert info["status"] == "not_authenticated"
        assert "message" in info


def test_get_workspace_auth_info_authenticated():
    """Valida a estrutura de diagnóstico quando o usuário possui sessão ativa."""
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.scopes = WORKSPACE_SCOPES
    mock_creds.expiry = "2026-09-03T12:00:00Z"
    mock_creds.refresh_token = "1//valid-refresh"

    with patch("shared.auth.workspace_auth.get_workspace_credentials", return_value=mock_creds), \
         patch("googleapiclient.discovery.build") as mock_build:
        mock_service = MagicMock()
        mock_userinfo = MagicMock()
        mock_userinfo.get.return_value.execute.return_value = {"email": "melkidonadonmed@gmail.com"}
        mock_service.userinfo.return_value = mock_userinfo
        mock_build.return_value = mock_service

        info = get_workspace_auth_info()
        assert info["authenticated"] is True
        assert info["status"] == "active"
        assert info["account"] == "melkidonadonmed@gmail.com"
        assert info["has_refresh_token"] is True


def test_update_env_file_preserves_content(tmp_path: Path):
    """Garante que a atualização do .env insere ou atualiza as variáveis sem corromper o arquivo."""
    fake_env = tmp_path / ".env"
    fake_env.write_text("EXISTING_KEY=123\n# Comentário\n", encoding="utf-8")

    with patch("shared.auth.workspace_auth.get_repo_root", return_value=tmp_path):
        update_env_file("client-123", "secret-456", "refresh-789")

    content = fake_env.read_text(encoding="utf-8")
    assert "EXISTING_KEY=123" in content
    assert "WORKSPACE_OAUTH_CLIENT_ID=client-123" in content
    assert "WORKSPACE_OAUTH_CLIENT_SECRET=secret-456" in content
    assert "WORKSPACE_OAUTH_REFRESH_TOKEN=refresh-789" in content
