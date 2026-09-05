"""Subagente especialista em inspeção e manipulação do workspace e projetos clientes (Stateless)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
        """Varre o projeto cliente especificado ou o workspace geral respeitando a profundidade máxima."""
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

        logger.info(f"WorkspaceSpecialist varrendo diretório: {scan_dir.as_posix()}")

        file_tree: list[str] = []
        tech_stack: list[str] = []
        is_target_project = scan_dir.resolve() != self.root_dir.resolve()

        # Detecção de stack tecnológica do projeto alvo
        try:
            pkg_file = scan_dir / "package.json"
            if pkg_file.exists():
                tech_stack.append("Node.js/npm")
                pkg_text = pkg_file.read_text(encoding="utf-8").lower()
                if "vite" in pkg_text:
                    tech_stack.append("Vite")
                if "react" in pkg_text:
                    tech_stack.append("React")
                if "tailwindcss" in pkg_text or "@tailwindcss" in pkg_text:
                    tech_stack.append("Tailwind CSS")
                if "typescript" in pkg_text:
                    tech_stack.append("TypeScript")
        except OSError:
            pass

        try:
            if (scan_dir / "pyproject.toml").exists() or (scan_dir / "requirements.txt").exists():
                tech_stack.append("Python")
            if (scan_dir / "go.mod").exists():
                tech_stack.append("Go")
        except OSError:
            pass

        try:
            for path in scan_dir.rglob("*"):
                # Ignora diretórios pesados e temporários
                if any(part in path.parts for part in [".venv", "node_modules", "__pycache__", ".git", "dist", ".brain", "artifacts"]):
                    continue
                try:
                    rel_path = path.relative_to(scan_dir)
                except ValueError:
                    rel_path = path

                if len(rel_path.parts) <= max_depth:
                    icon = "📁" if path.is_dir() else "📄"
                    file_tree.append(f"{icon} {rel_path.as_posix()}")
        except OSError as e:
            logger.error(f"Erro na varredura do diretório {scan_dir}: {e}")

        return {
            "agent": "WorkspaceSpecialistAgent",
            "root_path": scan_dir.as_posix(),
            "is_target_project": is_target_project,
            "tech_stack": tech_stack,
            "total_items_scanned": len(file_tree),
            "files": file_tree,
            "tree_preview": file_tree[:30],
            "status": "success",
        }
