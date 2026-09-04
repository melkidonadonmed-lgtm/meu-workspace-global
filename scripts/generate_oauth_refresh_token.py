"""Script utilitário para gerar o Refresh Token e Login Persistente no Google Workspace.

Executa o fluxo local de consentimento OAuth 2.0 no navegador para a conta pessoal
melkidonadonmed@gmail.com no projeto GCP agent-md-506215.

Salva o token permanentemente em configs/workspace_token.json e sincroniza o arquivo .env.

Uso:
    python scripts/generate_oauth_refresh_token.py
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para importação de shared
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from shared.auth.workspace_auth import login_workspace_interactive


def main() -> None:
    print("\n" + "=" * 60)
    print("🔐 INICIANDO LOGIN PERSISTENTE COM CONTA GOOGLE")
    print("=" * 60)
    result = login_workspace_interactive(open_browser=True)

    if result.get("status") == "success":
        print("\n" + "=" * 60)
        print("✅ AUTENTICAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"Conta: {result.get('account')}")
        print(f"Token salvo em: {result.get('token_path')}")
        print(f"Expiração: {result.get('expiry')}")
        print("As credenciais foram persistidas no arquivo de token e no .env.")
        print("=" * 60 + "\n")
    else:
        print("\n" + "=" * 60)
        print(f"❌ ERRO NA AUTENTICAÇÃO: {result.get('error')}")
        print("=" * 60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
