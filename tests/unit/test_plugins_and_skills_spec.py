"""Testes unitários para conformidade do modelo de Plugins e Skills do Antigravity CLI."""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"


def test_plugins_and_skills_docs_exist():
    """Garante que o guia técnico de Plugins e Skills está presente com as seções essenciais."""
    doc_path = REPO_ROOT / "docs" / "antigravity-plugins-and-skills.md"
    assert doc_path.exists(), "Documento docs/antigravity-plugins-and-skills.md não encontrado."

    text = doc_path.read_text(encoding="utf-8")
    assert "plugin.json" in text
    assert "https://antigravity.google/schemas/v1/plugin.json" in text
    assert "agy plugin list" in text
    assert "Slash Commands" in text
    assert "hooks.json" in text


def test_workspace_toolkit_plugin_manifest_conforms_to_schema():
    """Garante que o plugin workspace-toolkit possui um plugin.json estritamente em conformidade com o schema oficial."""
    manifest_path = PLUGINS_DIR / "workspace-toolkit" / "plugin.json"
    assert manifest_path.exists(), f"Manifesto não encontrado: {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Validação de campos obrigatórios
    assert "name" in data, "Campo 'name' é obrigatório no plugin.json."
    name = data["name"]

    # 2. Validação de padrão regex oficial (^[a-zA-Z0-9-_]+$)
    assert re.match(r"^[a-zA-Z0-9-_]+$", name), f"Nome do plugin '{name}' viola a regex ^[a-zA-Z0-9-_]+$."

    # 3. Validação de descrição
    desc = data.get("description", "")
    assert len(desc) >= 15, "Descrição do plugin muito curta."

    # 4. Validação de Schema URL
    assert data.get("$schema") == "https://antigravity.google/schemas/v1/plugin.json"


def test_plugin_skills_structure():
    """Valida que todas as skills dentro de plugins tenham frontmatter válido e descrição de qualidade."""
    skill_files = list(PLUGINS_DIR.glob("**/SKILL.md"))
    assert len(skill_files) >= 1, "Nenhuma skill encontrada no diretório de plugins."

    for skill_path in skill_files:
        content = skill_path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        assert match, f"Frontmatter ausente em {skill_path}."

        yaml_text = match.group(1)
        name_match = re.search(r"^name:\s*(.+)$", yaml_text, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)$", yaml_text, re.MULTILINE)

        assert name_match, f"Campo 'name' ausente no frontmatter de {skill_path}."
        assert desc_match, f"Campo 'description' ausente no frontmatter de {skill_path}."

        skill_name = name_match.group(1).strip().strip('"').strip("'")
        skill_desc = desc_match.group(1).strip().strip('"').strip("'")

        assert re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", skill_name), f"Nome '{skill_name}' deve estar em kebab-case."
        assert len(skill_desc) >= 20, f"Descrição de '{skill_name}' deve ter pelo menos 20 caracteres."
