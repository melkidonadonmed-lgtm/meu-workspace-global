"""Sincronizador e publicador do catálogo plano de skills (1 nível de profundidade).

Varre o catálogo estruturado em skills/ e gera a pasta published_skills/ contendo
junctions no Windows (ou symlinks) para cada skill folha válida, garantindo compatibilidade
nativa com Claude Code, OpenCode e ferramentas do protocolo Agent Skills.
"""

from __future__ import annotations

import io
import re
import subprocess
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = WORKSPACE_ROOT / "skills"
AGENTS_SKILLS_DIR = WORKSPACE_ROOT / ".agents" / "skills"
TARGET_DIR = WORKSPACE_ROOT / "published_skills"


def parse_skill_name(skill_file: Path) -> str | None:
    """Extrai o nome da skill a partir do frontmatter YAML."""
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return None

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None

    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"').strip("'")
            if re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
                return name
    return None


def create_dir_link(link_path: Path, target_path: Path) -> bool:
    """Cria uma Junction de diretório no Windows ou symlink em POSIX."""
    if link_path.exists():
        return False

    if sys.platform == "win32":
        link_str = str(link_path).replace("/", "\\")
        target_str = str(target_path).replace("/", "\\")
        cmd = f'cmd /c mklink /J "{link_str}" "{target_str}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        return res.returncode == 0

    link_path.symlink_to(target_path, target_is_directory=True)
    return True


def sync_catalog() -> int:
    """Sincroniza o catálogo plano e retorna a quantidade de skills vinculadas."""
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    search_dirs = [SKILLS_DIR]
    if AGENTS_SKILLS_DIR.exists() and AGENTS_SKILLS_DIR != SKILLS_DIR:
        search_dirs.append(AGENTS_SKILLS_DIR)

    indexed = 0
    seen_names: set[str] = set()

    for sdir in search_dirs:
        for skill_path in sorted(sdir.glob("**/SKILL.md")):
            parent = skill_path.parent
            skill_name = parse_skill_name(skill_path)

            if not skill_name or skill_name in seen_names:
                continue

            # Valida que o nome coincide com a pasta para respeitar o padrão de skill folha
            if skill_name != parent.name:
                continue

            dest_link = TARGET_DIR / skill_name
            if not dest_link.exists():
                if create_dir_link(dest_link, parent):
                    indexed += 1
            else:
                indexed += 1

            seen_names.add(skill_name)

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass
    print(f"[OK] Catalogo plano sincronizado: {len(seen_names)} skills ativas em {TARGET_DIR}")
    return len(seen_names)


if __name__ == "__main__":
    sync_catalog()
