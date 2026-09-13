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
from collections.abc import Iterable
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


def discover_skills() -> tuple[dict[str, Path], list[str]]:
    """Descobre skills válidas e retorna o índice por nome e os conflitos encontrados."""
    search_dirs = [SKILLS_DIR]
    if AGENTS_SKILLS_DIR.exists() and AGENTS_SKILLS_DIR != SKILLS_DIR:
        search_dirs.append(AGENTS_SKILLS_DIR)

    discovered: dict[str, Path] = {}
    conflicts: list[str] = []
    seen_names: set[str] = set()

    for sdir in search_dirs:
        for skill_path in sorted(sdir.glob("**/SKILL.md")):
            parent = skill_path.parent
            skill_name = parse_skill_name(skill_path)

            if not skill_name or skill_name in seen_names:
                if skill_name and skill_name in seen_names:
                    conflicts.append(f"{skill_name}: {skill_path}")
                continue

            # Valida que o nome coincide com a pasta para respeitar o padrão de skill folha
            if skill_name != parent.name:
                conflicts.append(f"{skill_name}: pasta esperada {skill_name}, encontrada {parent.name}")
                continue

            discovered[skill_name] = parent
            seen_names.add(skill_name)

    return discovered, conflicts


def _iter_existing_links() -> Iterable[Path]:
    if not TARGET_DIR.is_dir():
        return ()
    return (entry for entry in TARGET_DIR.iterdir() if entry.is_dir())


def sync_catalog(*, check_only: bool = False) -> int:
    """Sincroniza ou valida o catálogo plano e retorna a quantidade de skills válidas."""
    discovered, conflicts = discover_skills()
    stale_links = [entry.name for entry in _iter_existing_links() if entry.name not in discovered]

    if conflicts:
        for conflict in conflicts:
            print(f"[ERRO] Conflito de skill: {conflict}", file=sys.stderr)
        return 1

    if check_only:
        missing_links: list[str] = []
        divergent_links: list[str] = []
        for skill_name, skill_path in discovered.items():
            link_path = TARGET_DIR / skill_name
            if not link_path.is_dir():
                missing_links.append(skill_name)
                print(f"[CHECK] Ausente: {skill_name} -> {skill_path}")
            elif link_path.resolve() != skill_path.resolve():
                divergent_links.append(skill_name)
                print(f"[CHECK] Divergente: {skill_name} -> {link_path.resolve()}")
        for stale_name in stale_links:
            print(f"[CHECK] Obsoleto: {stale_name}")
        status = "OK" if not (missing_links or divergent_links or stale_links) else "FALHA"
        print(f"[{status}] Catalogo verificado: {len(discovered)} skills validas")
        return 0 if status == "OK" else 1

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    indexed = 0
    for skill_name, skill_path in discovered.items():
        dest_link = TARGET_DIR / skill_name
        if not dest_link.exists() and not create_dir_link(dest_link, skill_path):
            print(f"[ERRO] Falha ao vincular {skill_name} -> {skill_path}", file=sys.stderr)
            return 1
        indexed += 1

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass
    print(f"[OK] Catalogo plano sincronizado: {indexed} skills ativas em {TARGET_DIR}")
    return indexed


if __name__ == "__main__":
    sys.exit(sync_catalog(check_only="--check" in sys.argv))
