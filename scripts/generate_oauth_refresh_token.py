"""Script utilitário para gerar o Refresh Token OAuth 2.0 do Google Workspace.

Executa o fluxo local de consentimento no navegador para a conta pessoal
melkidonadonmed@gmail.com no projeto GCP agent-md-506215.

Uso:
    python scripts/generate_oauth_refresh_token.py [caminho_oauth_client.json]
"""

import sys
from pathlib import Path

from shared.auth.workspace_auth import WORKSPACE_SCOPES
from shared.logger import get_logger

logger = get_logger("OAuthGenerator")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    default_secret_path = repo_root / "configs" / "oauth_client_desktop.json"

    client_secret_file = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else default_secret_path
    )

    if not client_secret_file.exists():
        print(
            f"\n[AVISO] Arquivo de credenciais não encontrado: {client_secret_file}\n"
            "Baixe o arquivo JSON do cliente OAuth 2.0 (Tipo Desktop) no GCP Console:\n"
            "https://console.cloud.google.com/apis/credentials?project=agent-md-506215\n"
            f"E salve em: {default_secret_path}\n"
        )
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        print(f"[*] Iniciando fluxo OAuth 2.0 com: {client_secret_file}")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret_file), WORKSPACE_SCOPES
        )
        credentials = flow.run_local_server(port=0)

        print("\n" + "=" * 60)
        print("✅ AUTENTICAÇÃO CONCLUÍDA COM SUCESSO!")
        print("Adicione as seguintes linhas ao seu arquivo .env:")
        print("=" * 60)
        print(f"WORKSPACE_OAUTH_CLIENT_ID={credentials.client_id}")
        print(f"WORKSPACE_OAUTH_CLIENT_SECRET={credentials.client_secret}")
        print(f"WORKSPACE_OAUTH_REFRESH_TOKEN={credentials.refresh_token}")
        print("=" * 60 + "\n")
    except Exception as e:  # noqa: BLE001 - captura falha de execução de script standalone
        print(f"[ERRO] Falha durante a autenticação OAuth: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
