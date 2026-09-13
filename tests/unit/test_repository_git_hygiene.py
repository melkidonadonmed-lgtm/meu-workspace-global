"""Testes de higiene do repositório Git para evitar regressões no CI."""

import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def _tracked_gitlinks(ls_files_output: str) -> list[str]:
    """Extrai linhas de gitlinks (modo 160000) do output de `git ls-files -s`."""
    return [line for line in ls_files_output.splitlines() if line.startswith("160000 ")]


def test_tracked_gitlinks_filters_only_mode_160000():
    """Valida o parsing determinístico das entradas de gitlink."""
    output = "\n".join(
        [
            "100644 abc 0\tREADME.md",
            "160000 def 0\tmeu-workspace-global",
            "100755 ghi 0\tscripts/test.sh",
            "160000 jkl 0\tvendor/lib",
        ]
    )
    assert _tracked_gitlinks(output) == [
        "160000 def 0\tmeu-workspace-global",
        "160000 jkl 0\tvendor/lib",
    ]


def test_repository_has_no_gitlinks_tracked():
    """Garante que o índice não contenha gitlinks/submódulos acidentais."""
    if shutil.which("git") is None:
        pytest.skip("Git não está disponível no ambiente de teste.")

    result = subprocess.run(
        ["git", "ls-files", "-s"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    gitlinks = _tracked_gitlinks(result.stdout)
    assert gitlinks == [], f"Gitlinks inesperados no repositório: {gitlinks}"
