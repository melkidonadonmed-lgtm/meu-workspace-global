"""Teste de Healthcheck e Integridade de todas as Skills do Catálogo (SKILL.md)."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def parse_yaml_frontmatter(content: str) -> tuple[dict[str, str] | None, str | None]:
    """Extrai campos básicos do frontmatter YAML delimitado por ---."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None, "Frontmatter YAML ausente ou mal formatado."

    yaml_text = match.group(1)
    data: dict[str, str] = {}
    current_key = None
    multiline_value = []

    for line in yaml_text.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue

        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            if current_key and multiline_value:
                data[current_key] = " ".join(multiline_value).strip()
                multiline_value = []

            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val in (">", "|", ""):
                current_key = key
            else:
                data[key] = val
                current_key = None
        elif current_key and line.startswith((" ", "\t")):
            multiline_value.append(trimmed)

    if current_key and multiline_value:
        data[current_key] = " ".join(multiline_value).strip()

    return data, None


def test_all_skills_have_valid_structure():
    """Garante que todas as skills sob /skills sigam o padrão estrito de nomenclatura e metadados."""
    assert SKILLS_DIR.exists(), f"Diretório de skills não encontrado: {SKILLS_DIR}"

    skill_files = list(SKILLS_DIR.glob("**/SKILL.md"))
    assert len(skill_files) >= 5, "Nenhum arquivo SKILL.md encontrado no catálogo."

    errors = []

    for skill_path in skill_files:
        rel_path = skill_path.relative_to(REPO_ROOT).as_posix()
        folder_name = skill_path.parent.name
        content = skill_path.read_text(encoding="utf-8")

        # 1. Parsing do Frontmatter
        data, err = parse_yaml_frontmatter(content)
        if err or data is None:
            errors.append(f"[{rel_path}] {err}")
            continue

        # 2. Validação do atributo 'name'
        name = data.get("name")
        if not name:
            errors.append(f"[{rel_path}] Campo 'name' ausente no frontmatter YAML.")
        else:
            if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
                errors.append(f"[{rel_path}] 'name' ('{name}') não está em kebab-case.")
            if name != folder_name:
                errors.append(
                    f"[{rel_path}] 'name' ('{name}') difere do nome da pasta ('{folder_name}')."
                )

        # 3. Validação do atributo 'description'
        description = data.get("description", "")
        if not description or len(description) < 20:
            errors.append(
                f"[{rel_path}] 'description' ausente ou curta demais (< 20 caracteres)."
            )

    assert not errors, "Falhas de integridade no catálogo de skills:\n" + "\n".join(errors)
