"""Teste de Governança e Sincronização de Documentação (AGENTS.md, README.md, manifestos)."""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_MD = REPO_ROOT / "AGENTS.md"
README_MD = REPO_ROOT / "README.md"
MANIFEST_YAML = REPO_ROOT / "configs" / "agents_manifest.yaml"
SPECIALIZED_DIR = REPO_ROOT / "agents" / "specialized"


def test_specialized_agents_registered_in_governance_docs():
    """Garante que todos os subagentes criados em agents/specialized/ estejam registrados em AGENTS.md e manifestos."""
    assert AGENTS_MD.exists(), "AGENTS.md não encontrado na raiz."
    assert MANIFEST_YAML.exists(), "agents_manifest.yaml não encontrado em configs/."

    agents_md_text = AGENTS_MD.read_text(encoding="utf-8")
    manifest_data = yaml.safe_load(MANIFEST_YAML.read_text(encoding="utf-8"))

    # Coleta todos os subagentes em agents/specialized/*.py (exceto __init__.py)
    agent_files = [
        f.stem
        for f in SPECIALIZED_DIR.glob("*.py")
        if f.name != "__init__.py"
    ]

    assert len(agent_files) >= 3, "Nenhum subagente encontrado em agents/specialized/."

    allowed_subagents = manifest_data.get("orchestrator", {}).get("allowed_subagents", [])
    specialized_dict = manifest_data.get("specialized_agents", {})

    for agent_id in agent_files:
        # 1. Verifica presença no AGENTS.md
        assert agent_id in agents_md_text, (
            f"Subagente '{agent_id}' não está registrado em AGENTS.md!"
        )

        # 2. Verifica presença no agents_manifest.yaml
        assert agent_id in allowed_subagents, (
            f"Subagente '{agent_id}' não está na lista 'allowed_subagents' de agents_manifest.yaml!"
        )
        assert agent_id in specialized_dict, (
            f"Subagente '{agent_id}' não está declarado na seção 'specialized_agents' de agents_manifest.yaml!"
        )
