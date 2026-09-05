"""Resolução determinística de projetos-alvo em projects/ e detecção de stack tecnológica.

Extraído do antigo ExecutionPlanner (framework de orquestração descontinuado em 2026-09-05) —
esta parte era a única com lógica real e sem dependência de LLM, então sobrevive sozinha.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Mapeamento determinístico de projetos clientes em meu-workspace-global/projects
KNOWN_PROJECT_NAMES: dict[str, str] = {
    "pcm": "pcm",
    "prescmed": "pcm",
    "prescmed-v2": "pcm",
    "canvas_ide": "canvas_ide",
    "canvas": "canvas_ide",
    "keepdocs": "keepdocs-workspace",
    "keepdocs-workspace": "keepdocs-workspace",
    "waoe": "WAOE",
    "remix-prescmed-new": "remix-prescmed-new",
    "customer_issue_reviewer_go": "customer_issue_reviewer_go",
    "web_visual_auditor": "web_visual_auditor",
}


@dataclass
class ProjectTargetInfo:
    """Metadados do projeto alvo detectado na solicitação."""

    name: str
    target_path: Path
    exists: bool
    tech_stack: list[str] = field(default_factory=list)
    description: str = ""


CANONICAL_EXTERNAL_PROJECTS_DIR = Path("C:/Users/melki/Projetos")


class ProjectTargetResolver:
    """Localizador determinístico do diretório de projetos clientes (Projetos/ ou projects/)."""

    @staticmethod
    def resolve_target(user_input: str, workspace_root: Path | None = None) -> ProjectTargetInfo | None:
        text_lower = user_input.lower()
        root = workspace_root or Path(__file__).resolve().parents[1]
        local_projects_dir = root / "projects"

        # 1. Correspondência com projetos conhecidos no ecossistema
        for proj_alias, folder_name in sorted(KNOWN_PROJECT_NAMES.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = rf"\b{re.escape(proj_alias)}\b"
            if re.search(pattern, text_lower):
                # Prioridade 1: pasta canônica C:\Users\melki\Projetos
                target_path = CANONICAL_EXTERNAL_PROJECTS_DIR / folder_name
                # Fallback: pasta local do workspace projects/
                if not target_path.exists() and local_projects_dir.exists():
                    candidate = local_projects_dir / folder_name
                    if candidate.exists():
                        target_path = candidate

                tech_stack = ProjectTargetResolver._detect_tech_stack(target_path) if target_path.exists() else []
                return ProjectTargetInfo(
                    name=folder_name,
                    target_path=target_path,
                    exists=target_path.exists(),
                    tech_stack=tech_stack,
                    description=f"Projeto {folder_name} localizado em {target_path.as_posix()}",
                )

        # 2. Descoberta dinâmica em C:\Users\melki\Projetos e projects/ local
        search_dirs = [CANONICAL_EXTERNAL_PROJECTS_DIR, local_projects_dir]
        for pdir in search_dirs:
            if pdir.exists():
                for child in pdir.iterdir():
                    if (child.is_dir() or child.is_symlink()) and child.name.lower() in text_lower:
                        tech_stack = ProjectTargetResolver._detect_tech_stack(child)
                        return ProjectTargetInfo(
                            name=child.name,
                            target_path=child,
                            exists=True,
                            tech_stack=tech_stack,
                            description=f"Projeto descoberto em {child.as_posix()}",
                        )

        return None

    @staticmethod
    def _detect_tech_stack(project_path: Path) -> list[str]:
        """Inspeciona manifestos do projeto alvo para identificar a stack tecnológica."""
        stack: list[str] = []
        try:
            pkg_file = project_path / "package.json"
            if pkg_file.exists():
                stack.append("Node.js/npm")
                pkg_text = pkg_file.read_text(encoding="utf-8").lower()
                if "vite" in pkg_text:
                    stack.append("Vite")
                if "react" in pkg_text:
                    stack.append("React")
                if "tailwindcss" in pkg_text or "@tailwindcss" in pkg_text:
                    stack.append("Tailwind CSS")
                if "typescript" in pkg_text:
                    stack.append("TypeScript")
        except OSError:
            pass

        try:
            if (project_path / "pyproject.toml").exists() or (project_path / "requirements.txt").exists():
                stack.append("Python")
            if (project_path / "go.mod").exists():
                stack.append("Go")
        except OSError:
            pass

        return stack
