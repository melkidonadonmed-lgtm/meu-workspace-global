"""Gerenciamento de credenciais OAuth 2.0 persistentes para Google Workspace (Calendar, Gmail, Drive, Sheets, Docs)."""

import json
import os
import sys
from pathlib import Path
from typing import Any

from shared.logger import get_logger

logger = get_logger("WorkspaceAuth")

WORKSPACE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def get_repo_root() -> Path:
    """Retorna o diretório raiz do repositório meu-workspace-global."""
    return Path(__file__).resolve().parent.parent.parent


def get_token_storage_path() -> Path:
    """Retorna o caminho do arquivo de token persistente."""
    repo_root = get_repo_root()
    return repo_root / "configs" / "workspace_token.json"


def get_client_secrets_path() -> Path | None:
    """Localiza o arquivo de credenciais do cliente OAuth Desktop no diretório configs."""
    repo_root = get_repo_root()
    candidates = [
        Path(os.getenv("WORKSPACE_CREDENTIALS_FILE", "")),
        repo_root / "configs" / "credentials.json",
        repo_root / "configs" / "oauth_client_desktop.json",
    ]
    for path in candidates:
        if path and path.is_file():
            return path
    return None


def save_credentials_to_file(credentials: Any, token_path: Path | None = None) -> Path:
    """Salva credenciais OAuth autorizadas em formato JSON persistente."""
    dest_path = token_path or get_token_storage_path()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(credentials.to_json())
    logger.info(f"Token OAuth persistente salvo em: {dest_path}")
    return dest_path


def update_env_file(client_id: str, client_secret: str, refresh_token: str) -> None:
    """Atualiza o arquivo .env do repositório com as variáveis OAuth permanentes."""
    repo_root = get_repo_root()
    env_path = repo_root / ".env"

    lines: list[str] = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    keys_to_update = {
        "WORKSPACE_OAUTH_CLIENT_ID": client_id,
        "WORKSPACE_OAUTH_CLIENT_SECRET": client_secret,
        "WORKSPACE_OAUTH_REFRESH_TOKEN": refresh_token,
    }

    updated_keys = set()
    new_lines: list[str] = []

    for line in lines:
        matched = False
        for key, val in keys_to_update.items():
            if line.startswith((f"{key}=", f"#{key}=")):
                new_lines.append(f"{key}={val}\n")
                updated_keys.add(key)
                matched = True
                break
        if not matched:
            new_lines.append(line)

    for key, val in keys_to_update.items():
        if key not in updated_keys:
            if new_lines and not new_lines[-1].endswith("\n"):
                new_lines.append("\n")
            new_lines.append(f"{key}={val}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    logger.info(f"Arquivo .env atualizado com credenciais OAuth em: {env_path}")


def get_workspace_credentials(scopes: list[str] | None = None) -> Any:
    """Obtém credenciais OAuth 2.0 persistentes e válidas para a conta Google do usuário.

    Verifica em camadas:
    1. Arquivo de token persistente (configs/workspace_token.json) com renovação automática se expirado.
    2. Variáveis de ambiente WORKSPACE_OAUTH_* (.env).
    Retorna objeto google.oauth2.credentials.Credentials ou None se não autenticado.
    """
    token_path = get_token_storage_path()
    target_scopes = scopes or WORKSPACE_SCOPES

    # 1. Carregamento a partir do token.json persistente
    if token_path.is_file():
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials

            credentials = Credentials.from_authorized_user_file(
                str(token_path), scopes=target_scopes
            )
            if credentials:
                if credentials.expired and credentials.refresh_token:
                    logger.info("Token Google Workspace expirado. Renovando automaticamente via Refresh Token...")
                    credentials.refresh(Request())
                    save_credentials_to_file(credentials, token_path)
                if credentials.valid:
                    return credentials
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Falha ao carregar/renovar token persistente de {token_path}: {e}")

    # 2. Carregamento via variáveis de ambiente (.env)
    client_id = os.getenv("WORKSPACE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("WORKSPACE_OAUTH_CLIENT_SECRET")
    refresh_token = os.getenv("WORKSPACE_OAUTH_REFRESH_TOKEN")

    if client_id and client_secret and refresh_token:
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials

            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=target_scopes,
            )
            if credentials.expired or not credentials.token:
                logger.info("Obtendo access_token a partir do WORKSPACE_OAUTH_REFRESH_TOKEN...")
                credentials.refresh(Request())
                save_credentials_to_file(credentials, token_path)

            if credentials.valid:
                return credentials
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Erro ao instanciar credenciais OAuth via .env: {e}")

    logger.debug(
        "Nenhuma credencial Google Workspace ativa encontrada. "
        "Execute 'login_google_workspace' para autenticar sua conta Google de forma persistente."
    )
    return None


def login_workspace_interactive(
    scopes: list[str] | None = None,
    port: int = 0,
    open_browser: bool = True,
) -> dict[str, Any]:
    """Executa o fluxo de autenticação OAuth 2.0 no navegador e salva os tokens de forma permanente."""
    secret_file = get_client_secrets_path()
    target_scopes = scopes or WORKSPACE_SCOPES

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        flow: InstalledAppFlow
        if secret_file:
            logger.info(f"Iniciando fluxo OAuth com arquivo: {secret_file}")
            flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), target_scopes)
        else:
            client_id = os.getenv("WORKSPACE_OAUTH_CLIENT_ID")
            client_secret = os.getenv("WORKSPACE_OAUTH_CLIENT_SECRET")
            if not (client_id and client_secret):
                return {
                    "status": "error",
                    "error": (
                        "Arquivo de credenciais (credentials.json) não encontrado em configs/ "
                        "e variáveis WORKSPACE_OAUTH_CLIENT_ID / SECRET não definidas."
                    ),
                }
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, target_scopes)

        logger.info("[*] Abrindo navegador para autorização da sua conta Google Workspace...")
        credentials = flow.run_local_server(port=port, open_browser=open_browser)

        token_path = save_credentials_to_file(credentials)
        if credentials.refresh_token:
            update_env_file(
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                refresh_token=credentials.refresh_token,
            )

        account_email = "autenticado"
        try:
            from googleapiclient.discovery import build

            oauth2_service = build("oauth2", "v2", credentials=credentials)
            user_info = oauth2_service.userinfo().get().execute()
            account_email = user_info.get("email", "autenticado")
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Não foi possível obter email de userinfo: {e}")

        return {
            "status": "success",
            "message": f"Login persistente concluído com sucesso para a conta {account_email}!",
            "account": account_email,
            "token_path": str(token_path),
            "scopes": credentials.scopes or target_scopes,
            "expiry": str(credentials.expiry) if credentials.expiry else None,
        }

    except Exception as e:
        logger.exception("Erro durante o fluxo interativo de autenticação")
        return {
            "status": "error",
            "error": f"Falha na autenticação OAuth: {e!s}",
        }


def get_workspace_auth_info() -> dict[str, Any]:
    """Retorna informações e diagnóstico sobre o estado atual da autenticação com o Google Workspace."""
    token_path = get_token_storage_path()
    credentials = get_workspace_credentials()

    if credentials and credentials.valid:
        account_email = "desconhecido"
        try:
            from googleapiclient.discovery import build

            oauth2_service = build("oauth2", "v2", credentials=credentials)
            user_info = oauth2_service.userinfo().get().execute()
            account_email = user_info.get("email", "desconhecido")
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Não foi possível obter email de userinfo: {e}")

        return {
            "authenticated": True,
            "status": "active",
            "account": account_email,
            "scopes": credentials.scopes or WORKSPACE_SCOPES,
            "token_storage": str(token_path),
            "expiry": str(credentials.expiry) if credentials.expiry else None,
            "has_refresh_token": bool(credentials.refresh_token),
        }

    return {
        "authenticated": False,
        "status": "not_authenticated",
        "message": (
            "Conta Google Workspace não autenticada. "
            "Execute a ferramenta 'login_google_workspace' ou o comando "
            "'python -m shared.auth.workspace_auth login' para fazer login persistente."
        ),
        "token_storage_path": str(token_path),
        "token_file_exists": token_path.is_file(),
        "client_secrets_found": get_client_secrets_path() is not None,
    }


def main():
    """CLI para gerenciar autenticação Google Workspace."""
    action = sys.argv[1] if len(sys.argv) > 1 else "status"

    if action == "login":
        print("[*] Iniciando processo de login persistente...")
        result = login_workspace_interactive()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif action == "status":
        info = get_workspace_auth_info()
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print(f"Comando desconhecido: {action}. Use 'login' ou 'status'.")


if __name__ == "__main__":
    main()
