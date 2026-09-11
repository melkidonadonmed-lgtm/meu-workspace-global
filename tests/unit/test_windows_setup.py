"""Testes unitários para documentação e scripts de configuração e diagnóstico do Windows."""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_windows_setup_docs_exist():
    """Garante que a documentação técnica de Windows está presente e possui as seções canônicas."""
    doc_path = REPO_ROOT / "docs" / "antigravity-windows-setup.md"
    assert doc_path.exists(), "Documento docs/antigravity-windows-setup.md não encontrado."

    text = doc_path.read_text(encoding="utf-8")
    assert "AppData\\Local\\agy\\bin" in text
    assert "install.ps1" in text
    assert "install.cmd" in text
    assert "--skip-aliases" in text
    assert "--skip-path" in text
    assert "Windows Credential Manager" in text


def test_windows_diagnostic_script_exists_and_valid():
    """Garante que o script de diagnóstico de ambiente Windows existe e possui a estrutura esperada."""
    script_path = REPO_ROOT / "scripts" / "check-windows-environment.ps1"
    assert script_path.exists(), "Script scripts/check-windows-environment.ps1 não encontrado."

    script_text = script_path.read_text(encoding="utf-8")
    assert "agy.exe" in script_text
    assert "antigravity.cmd" in script_text
    assert "[switch]$Fix" in script_text
    assert "LOCALAPPDATA" in script_text


def test_canonical_windows_binary_location():
    """Valida a resolução do caminho canônico de instalação no ambiente Windows."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    assert local_app_data is not None, "Variável de ambiente LOCALAPPDATA não definida."

    bin_dir = Path(local_app_data) / "agy" / "bin"
    agy_exe = bin_dir / "agy.exe"
    antigravity_cmd = bin_dir / "antigravity.cmd"

    # No ambiente de desenvolvimento de Melki, esses binários devem estar presentes
    assert agy_exe.exists(), f"Executável oficial não encontrado em: {agy_exe}"
    assert antigravity_cmd.exists(), f"Arquivo batch oficial não encontrado em: {antigravity_cmd}"
