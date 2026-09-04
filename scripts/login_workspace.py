"""Atalho executável para realizar login persistente com a conta Google Workspace.

Uso:
    python scripts/login_workspace.py
"""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from scripts.generate_oauth_refresh_token import main

if __name__ == "__main__":
    main()
