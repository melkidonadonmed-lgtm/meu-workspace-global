"""Subagente especialista em inspeção e manipulação do workspace e projetos clientes (Stateless)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.project_resolver import ProjectTargetResolver
from shared.logger import get_logger

logger = get_logger("WorkspaceSpecialist")


class WorkspaceSpecialistAgent:
    """Especialista stateless em estrutura de diretórios, rotas e integridade de arquivos."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()

    def scan_workspace(
        self,
        target_path: str | Path | None = None,
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """Varre o projeto cliente especificado ou o workspace delegando ao ProjectTargetResolver."""
        scan_dir: Path
        if target_path:
            p = Path(target_path)
            if p.is_absolute() and p.exists():
                scan_dir = p
            elif (self.root_dir / str(target_path)).exists():
                scan_dir = (self.root_dir / str(target_path)).resolve()
            elif p.exists():
                scan_dir = p.resolve()
            else:
                scan_dir = self.root_dir
        else:
            scan_dir = self.root_dir

        logger.info(f"WorkspaceSpecialist delegando varredura para ProjectTargetResolver: {scan_dir.as_posix()}")

        # Delegação profunda para o Deep Module ProjectTargetResolver
        result = ProjectTargetResolver.scan_directory(scan_dir, max_depth=max_depth)
        result["agent"] = "WorkspaceSpecialistAgent"
        result["is_target_project"] = scan_dir.resolve() != self.root_dir.resolve()
        return result

