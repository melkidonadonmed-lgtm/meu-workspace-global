"""Fixtures compartilhadas e utilitários auxiliares para a suíte E2E do ecossistema."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Caminhos canônicos do ecossistema
HUB_GEMINI_DIR = Path(r"C:\Users\melki\.gemini")
CANONICAL_PROJECTS_DIR = Path(r"C:\Users\melki\Projetos")
WORKSPACE_ROOT = Path(r"C:\Users\melki\meu-workspace-global")
CANONICAL_PROJECTS_JSON = HUB_GEMINI_DIR / "projects.json"
CANONICAL_HOOK_SCRIPT = HUB_GEMINI_DIR / "scripts" / "hooks" / "pre_tool_guard.py"
WORKSPACE_HOOK_SCRIPT = WORKSPACE_ROOT / "scripts" / "hooks" / "pre_tool_guard.py"
DASHBOARD_SCRIPT = HUB_GEMINI_DIR / "scripts" / "projects_dashboard.py"
HEALTHCHECK_SCRIPT = HUB_GEMINI_DIR / "scripts" / "ecosystem_healthcheck.py"


def run_hook_subprocess(script_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Executa um script de hook via subprocess passando JSON via stdin e capturando stdout."""
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        input=json.dumps(payload),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    stdout_clean = proc.stdout.strip()
    return json.loads(stdout_clean)


@pytest.fixture
def run_hook():
    """Fixture que fornece o invocador de hook via subprocess."""
    return run_hook_subprocess


@pytest.fixture
def sample_node_manifest(tmp_path: Path) -> Path:
    """Gera um projeto temporário com package.json contendo React e Vite."""
    proj = tmp_path / "sample_react_app"
    proj.mkdir(parents=True, exist_ok=True)
    pkg = {
        "name": "sample-react-app",
        "version": "1.0.0",
        "dependencies": {
            "react": "^19.0.0",
            "react-dom": "^19.0.0",
        },
        "devDependencies": {
            "vite": "^5.0.0",
            "typescript": "^5.2.0",
            "tailwindcss": "^3.4.0",
        },
    }
    (proj / "package.json").write_text(json.dumps(pkg, indent=2), encoding="utf-8")
    return proj


@pytest.fixture
def sample_python_manifest(tmp_path: Path) -> Path:
    """Gera um projeto temporário com pyproject.toml."""
    proj = tmp_path / "sample_python_app"
    proj.mkdir(parents=True, exist_ok=True)
    toml_content = """[project]
name = "sample-python-app"
version = "0.1.0"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn>=0.28.0",
]
"""
    (proj / "pyproject.toml").write_text(toml_content, encoding="utf-8")
    return proj


@pytest.fixture
def sample_go_manifest(tmp_path: Path) -> Path:
    """Gera um projeto temporário com go.mod."""
    proj = tmp_path / "sample_go_app"
    proj.mkdir(parents=True, exist_ok=True)
    go_mod_content = """module github.com/melki/sample-go-app

go 1.22
"""
    (proj / "go.mod").write_text(go_mod_content, encoding="utf-8")
    return proj
