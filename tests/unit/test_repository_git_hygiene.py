"""Testes de higiene do repositório Git para evitar regressões no CI."""

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_repository_has_no_gitlinks_tracked():
    """Garante que o índice não contenha gitlinks/submódulos acidentais."""
    result = subprocess.run(
        ["git", "ls-files", "-s"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    gitlinks = [line for line in result.stdout.splitlines() if line.startswith("160000 ")]
    assert gitlinks == [], f"Gitlinks inesperados no repositório: {gitlinks}"
