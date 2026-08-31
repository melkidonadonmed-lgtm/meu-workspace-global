"""Subagente especialista em inspeção e manipulação do workspace/arquivos (Stateless)."""

from pathlib import Path
from typing import Any

from shared.logger import get_logger

logger = get_logger("WorkspaceSpecialist")


class WorkspaceSpecialistAgent:
    """Especialista stateless em estrutura de diretórios, rotas e integridade de arquivos."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def scan_workspace(self, max_depth: int = 3) -> dict[str, Any]:
        """Varre o workspace respeitando a profundidade máxima para diagnóstico rápido."""
        logger.info(f"WorkspaceSpecialist varrendo diretório: {self.root_dir.resolve()}")
        
        file_tree: list[str] = []
        try:
            for path in self.root_dir.rglob("*"):
                # Ignora diretórios pesados e temporários
                if any(part in path.parts for part in [".venv", "node_modules", "__pycache__", ".git"]):
                    continue
                rel_path = path.relative_to(self.root_dir)
                if len(rel_path.parts) <= max_depth:
                    icon = "📁" if path.is_dir() else "📄"
                    file_tree.append(f"{icon} {rel_path.as_posix()}")
        except OSError as e:
            logger.error(f"Erro na varredura do workspace: {e}")

        return {
            "agent": "WorkspaceSpecialistAgent",
            "root_path": str(self.root_dir.resolve()),
            "total_items_scanned": len(file_tree),
            "tree_preview": file_tree[:40],
            "status": "success"
        }
