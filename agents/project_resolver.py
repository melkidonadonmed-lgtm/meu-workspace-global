"""Deep Module para resolução determinística de projetos, aliases e detecção profunda de stack tecnológica.

Consome a Single Source of Truth (SSoT) canônica em C:\\Users\\melki\\.gemini\\projects.json,
mapeia junctions NTFS em meu-workspace-global/projects e suporta monorepos e manifestos
avançados (package.json, pyproject.toml, go.mod).
"""

from __future__ import annotations

import json
import os
import re
import stat
import tomllib
from pathlib import Path
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from shared.logger import get_logger

logger = get_logger("ProjectTargetResolver")

# Caminhos canônicos do ecossistema
CANONICAL_PROJECTS_JSON = Path(r"C:\Users\melki\.gemini\projects.json")
CANONICAL_EXTERNAL_PROJECTS_DIR = Path(r"C:\Users\melki\Projetos")

# Aliases canônicos históricos para compatibilidade retroativa direta
KNOWN_PROJECT_NAMES: dict[str, str] = {
    "pcm": "pcm",
    "prescmed": "pcm",
    "prescmed-v2": "pcm",
    "prescmed-pcm": "pcm",
    "canvas_ide": "mdk",
    "canvas-ide": "mdk",
    "canvas": "mdk",
    "keepdocs": "mdk",
    "keepdocs-workspace": "mdk",
    "waoe": "WAOE",
    "WAOE": "WAOE",
    "remix-prescmed-new": "remix-prescmed-new",
    "remix-prescmed": "remix-prescmed-new",
    "remix": "remix-prescmed-new",
    "tactile-ui-studio": "tactile-ui-studio",
    "tactile_ui_studio": "tactile-ui-studio",
    "tactile": "tactile-ui-studio",
    "atlas-ui-kit": "tactile-ui-studio",
    "customer_issue_reviewer_go": "customer_issue_reviewer_go",
    "customer_issue_reviewer": "customer_issue_reviewer_go",
    "customer-issue-reviewer": "customer_issue_reviewer_go",
    "web_visual_auditor": "web_visual_auditor",
    "web-visual-auditor": "web_visual_auditor",
    "mdk-teste": "mdk-teste",
    "mdk_teste": "mdk-teste",
    "mdk": "mdk",
    "mdk-cockpit": "mdk",
    "wise-galileo": "wise-galileo",
    "wise_galileo": "wise-galileo",
    "meu-workspace-global": "meu-workspace-global",
    "workspace-global": "meu-workspace-global",
}

# Metadados enriquecidos para exibição, portas e particularidades estruturais
KNOWN_METADATA: dict[str, dict[str, Any]] = {
    "pcm": {
        "display_name": "PresCMed (PCM)",
        "port": 3000,
        "aliases": ["pcm", "prescmed", "prescmed-pcm", "prescmed-v2"],
        "category": "client_project",
    },
    "WAOE": {
        "display_name": "WAOE Orchestrator",
        "port": 3001,
        "aliases": ["waoe", "WAOE"],
        "category": "client_project",
    },
    "waoe": {
        "display_name": "WAOE Orchestrator",
        "port": 3001,
        "aliases": ["waoe", "WAOE"],
        "category": "client_project",
    },
    "keepdocs-workspace": {
        "display_name": "KeepDocs Workspace",
        "port": 3002,
        "aliases": ["keepdocs-workspace", "keepdocs_workspace", "keepdocs"],
        "category": "client_project",
    },
    "remix-prescmed-new": {
        "display_name": "PresCMed Remix (Variante)",
        "port": 3003,
        "aliases": ["remix-prescmed-new", "remix-prescmed", "remix"],
        "category": "client_project",
    },
    "tactile-ui-studio": {
        "display_name": "Tactile UI Studio (Atlas)",
        "port": 4173,
        "aliases": ["tactile-ui-studio", "tactile_ui_studio", "tactile", "atlas-ui-kit", "atlas"],
        "subpath": "apps/atlas-ui-kit",
        "category": "client_project",
    },
    "mdk": {
        "display_name": "MDK Multi-Agent Canvas Stack",
        "port": 3000,
        "aliases": ["mdk", "mdk-cockpit", "canvas_ide", "canvas-ide", "canvas", "keepdocs", "keepdocs-workspace"],
        "category": "client_project",
    },
    "canvas_ide": {
        "display_name": "Canvas IDE",
        "port": 5173,
        "aliases": ["canvas_ide", "canvas-ide", "canvas"],
        "category": "client_project",
    },
    "canvas-ide": {
        "display_name": "Canvas IDE",
        "port": 5173,
        "aliases": ["canvas_ide", "canvas-ide", "canvas"],
        "category": "client_project",
    },
    "web_visual_auditor": {
        "display_name": "Web Visual Auditor",
        "port": None,
        "aliases": ["web_visual_auditor", "web-visual-auditor"],
        "category": "internal_tool",
    },
    "customer_issue_reviewer_go": {
        "display_name": "Customer Issue Reviewer (Go)",
        "port": None,
        "aliases": ["customer_issue_reviewer_go", "customer-issue-reviewer", "customer_issue_reviewer"],
        "category": "internal_tool",
    },
    "mdk-teste": {
        "display_name": "MDK Teste (Datacloud Pipeline)",
        "port": None,
        "aliases": ["mdk-teste", "mdk_teste", "mdk"],
        "category": "internal_tool",
    },
    "wise-galileo": {
        "display_name": "Wise Galileo Knowledge Base",
        "port": None,
        "aliases": ["wise-galileo", "wise_galileo"],
        "category": "knowledge_base",
    },
    "meu-workspace-global": {
        "display_name": "Meu Workspace Global",
        "port": None,
        "aliases": ["meu-workspace-global", "workspace-global", "workspace"],
        "category": "workspace",
    },
}


def is_ntfs_junction(path: Path) -> bool:
    """Detecta confiavelmente se um caminho no Windows é um ponto de junção NTFS (reparse point)."""
    if not path.exists():
        return False
    try:
        st = os.stat(path, follow_symlinks=False)
        return bool(st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (OSError, AttributeError):
        return False


class ManifestInfo(BaseModel):
    """Metadados extraídos de um arquivo de manifesto."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    manifest_type: str  # package.json, pyproject.toml, go.mod, requirements.txt
    path: Path
    package_name: str | None = None
    version: str | None = None
    scripts: dict[str, str] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    dev_dependencies: list[str] = Field(default_factory=list)

    def __init__(self, *args: Any, **data: Any):
        if args:
            names = [
                "manifest_type",
                "path",
                "package_name",
                "version",
                "scripts",
                "dependencies",
                "dev_dependencies",
            ]
            for n, v in zip(names, args):
                data[n] = v
        super().__init__(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class StackDetails(BaseModel):
    """Detalhamento profundo da stack tecnológica."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    primary_language: str = "Unknown"  # TypeScript, JavaScript, Python, Go, Unknown
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)  # React, React 19, Vite, Tailwind CSS, Express, etc.
    manifest_type: str = ""  # package.json, pyproject.toml, go.mod
    package_name: str | None = None
    dev_command: str | None = None
    package_manager: str | None = None  # npm, pnpm, yarn, bun, uv, poetry, pip
    default_port: int | None = None
    manifests: list[ManifestInfo] = Field(default_factory=list)

    def __init__(self, *args: Any, **data: Any):
        if args:
            names = [
                "primary_language",
                "languages",
                "frameworks",
                "manifest_type",
                "package_name",
                "dev_command",
                "package_manager",
                "default_port",
                "manifests",
            ]
            for n, v in zip(names, args):
                data[n] = v
        super().__init__(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class ProjectTargetInfo(BaseModel):
    """Metadados consolidados do projeto alvo."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    key: str
    name: str
    canonical_path: Path
    display_name: str = ""
    target_path: Path | None = None
    junction_path: Path | None = None
    local_junction_path: Path | None = None
    is_junction: bool = False
    exists: bool = False
    subpath: str | None = None
    stack: StackDetails = Field(default_factory=StackDetails)
    stack_details: StackDetails | None = None
    tech_stack: list[str] = Field(default_factory=list)
    port: int | None = None
    env_file_exists: bool = False
    category: str = "client_project"
    description: str = ""
    aliases: list[str] = Field(default_factory=list)

    def __init__(self, *args: Any, **data: Any):
        if args:
            names = [
                "key",
                "name",
                "canonical_path",
                "display_name",
                "target_path",
                "junction_path",
                "local_junction_path",
                "is_junction",
                "exists",
                "subpath",
                "stack",
                "stack_details",
                "tech_stack",
                "port",
                "env_file_exists",
                "category",
                "description",
                "aliases",
            ]
            for n, v in zip(names, args):
                data[n] = v
        super().__init__(**data)

    @model_validator(mode="after")
    def sync_legacy_fields(self) -> Self:
        if self.target_path is None:
            self.target_path = self.canonical_path
        if self.local_junction_path is None:
            self.local_junction_path = self.junction_path
        elif self.junction_path is None:
            self.junction_path = self.local_junction_path
        if self.stack_details is None:
            self.stack_details = self.stack
        elif self.stack is None:
            self.stack = self.stack_details
        if not self.display_name:
            self.display_name = self.name

        # Preencher tech_stack com tags formatadas se estiver vazio
        if not self.tech_stack and self.stack:
            tags: list[str] = []
            if self.stack.primary_language in ("TypeScript", "JavaScript"):
                tags.append("Node.js/npm")
                for fw in self.stack.frameworks:
                    if fw not in tags:
                        tags.append(fw)
                if self.stack.primary_language not in tags:
                    tags.append(self.stack.primary_language)
            elif self.stack.primary_language == "Python":
                tags.append("Python")
                for fw in self.stack.frameworks:
                    if fw not in tags:
                        tags.append(fw)
            elif self.stack.primary_language == "Go":
                tags.append("Go")
                for fw in self.stack.frameworks:
                    if fw not in tags:
                        tags.append(fw)
            self.tech_stack = tags
        return self

    def to_dict(self) -> dict[str, Any]:
        """Serialização amigável para JSON e consumo por dashboards e CLI."""
        return {
            "key": self.key,
            "name": self.display_name or self.name,
            "slug": self.key,
            "target_path": self.target_path.as_posix() if self.target_path else "",
            "canonical_path": self.canonical_path.as_posix() if self.canonical_path else "",
            "local_junction_path": self.local_junction_path.as_posix() if self.local_junction_path else None,
            "junction_path": self.junction_path.as_posix() if self.junction_path else None,
            "is_junction": self.is_junction,
            "exists": self.exists,
            "category": self.category,
            "tech_stack": self.tech_stack,
            "port": self.port,
            "default_port": self.port,
            "dev_command": self.stack.dev_command,
            "subpath": self.subpath,
            "has_env": self.env_file_exists,
            "aliases": self.aliases,
            "description": self.description,
            "stack": self.stack.model_dump(),
        }



class ProjectTargetResolver:
    """Deep Module para resolução determinística de projetos clientes e inspeção de stack."""

    CANONICAL_PROJECTS_JSON = CANONICAL_PROJECTS_JSON
    CANONICAL_EXTERNAL_PROJECTS_DIR = CANONICAL_EXTERNAL_PROJECTS_DIR
    _projects_cache: ClassVar[dict[tuple[str, bool, tuple[Any, ...]], list[ProjectTargetInfo]]] = {}

    @classmethod
    def clear_cache(cls) -> None:
        """Descarta o registro derivado para refletir alterações no ecossistema."""
        cls._projects_cache.clear()

    @classmethod
    def _registry_signature(cls, root: Path) -> tuple[Any, ...]:
        """Retorna uma assinatura barata dos metadados que controlam o registro."""
        watched_paths = [
            cls.CANONICAL_PROJECTS_JSON,
            cls.CANONICAL_EXTERNAL_PROJECTS_DIR,
            root / "projects",
        ]
        signature: list[Any] = []
        for path in watched_paths:
            try:
                stat_result = path.stat()
                signature.append((str(path), stat_result.st_mtime_ns, stat_result.st_size))
            except OSError:
                signature.append((str(path), None, None))

        for projects_dir in (cls.CANONICAL_EXTERNAL_PROJECTS_DIR, root / "projects"):
            if not projects_dir.is_dir():
                continue
            try:
                children = sorted(child for child in projects_dir.iterdir() if child.is_dir())
            except OSError:
                continue
            for child in children:
                signature.append((str(child), child.stat().st_mtime_ns))
                for manifest_name in ("package.json", "pyproject.toml", "requirements.txt", "go.mod"):
                    manifest = child / manifest_name
                    try:
                        signature.append((str(manifest), manifest.stat().st_mtime_ns, manifest.stat().st_size))
                    except OSError:
                        pass
        return tuple(signature)

    @classmethod
    def _extract_tech_stack_tags(cls, stack: StackDetails) -> list[str]:
        """Gera a lista resumida de tags para compatibilidade retroativa."""
        tags: list[str] = []
        if stack.primary_language in ("TypeScript", "JavaScript"):
            tags.append("Node.js/npm")
            for fw in stack.frameworks:
                if fw not in tags:
                    tags.append(fw)
            if stack.primary_language not in tags:
                tags.append(stack.primary_language)
        elif stack.primary_language == "Python":
            tags.append("Python")
            for fw in stack.frameworks:
                if fw not in tags:
                    tags.append(fw)
        elif stack.primary_language == "Go":
            tags.append("Go")
            for fw in stack.frameworks:
                if fw not in tags:
                    tags.append(fw)
        return tags

    @classmethod
    def _detect_tech_stack(cls, project_path: Path) -> list[str]:
        """Inspeciona manifestos do projeto alvo para identificar a stack tecnológica resumida."""
        details = cls.detect_stack(project_path)
        return cls._extract_tech_stack_tags(details)

    @classmethod
    def detect_stack(cls, directory: Path) -> StackDetails:
        """Realiza inspeção profunda de manifests (package.json, pyproject.toml, go.mod).

        Identifica linguagens primárias, frameworks reais, gerenciadores de pacotes,
        comandos de desenvolvimento e suporta subpastas de monorepo.
        """
        if not directory.exists() or not directory.is_dir():
            return StackDetails(primary_language="Unknown", manifest_type="", dev_command=None)

        # Se for monorepo ou se os manifests estiverem em subpasta conhecida (ex: apps/atlas-ui-kit)
        inspect_dir = directory
        subpaths_to_check = ["apps/atlas-ui-kit", "apps", "packages", "src"]
        if not (inspect_dir / "package.json").exists() and not (inspect_dir / "pyproject.toml").exists() and not (inspect_dir / "go.mod").exists():
            for sub in subpaths_to_check:
                candidate = inspect_dir / sub
                if candidate.exists() and candidate.is_dir():
                    if (candidate / "package.json").exists() or (candidate / "pyproject.toml").exists():
                        inspect_dir = candidate
                        break
                    # Checar subpastas imediatas de apps/
                    for child in candidate.iterdir():
                        if child.is_dir() and ((child / "package.json").exists() or (child / "pyproject.toml").exists()):
                            inspect_dir = child
                            break
                    if inspect_dir != directory:
                        break

        manifests: list[ManifestInfo] = []
        frameworks: list[str] = []
        languages: list[str] = []
        primary_language = "Unknown"
        manifest_type = ""
        package_name: str | None = None
        dev_command: str | None = None
        package_manager: str | None = None
        default_port: int | None = None

        # 1. Inspeção de package.json (Node.js / TypeScript / React / Vite)
        pkg_file = inspect_dir / "package.json"
        if pkg_file.exists():
            manifest_type = "package.json"
            pkg_data: dict[str, Any] = {}
            raw_text = ""
            try:
                raw_text = pkg_file.read_text(encoding="utf-8")
                pkg_data = json.loads(raw_text)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as err:
                logger.debug("Falha ao ler package.json em %s: %s", pkg_file, err)

            package_name = pkg_data.get("name")
            scripts = pkg_data.get("scripts", {}) if isinstance(pkg_data, dict) else {}
            deps_dict = pkg_data.get("dependencies", {}) if isinstance(pkg_data, dict) else {}
            dev_deps_dict = pkg_data.get("devDependencies", {}) if isinstance(pkg_data, dict) else {}

            all_deps = {**deps_dict, **dev_deps_dict}
            deps_keys = {k.lower() for k in all_deps}
            raw_lower = raw_text.lower()

            manifests.append(
                ManifestInfo(
                    manifest_type="package.json",
                    path=pkg_file,
                    package_name=package_name,
                    version=pkg_data.get("version"),
                    scripts={str(k): str(v) for k, v in scripts.items()},
                    dependencies=list(deps_dict.keys()),
                    dev_dependencies=list(dev_deps_dict.keys()),
                )
            )

            # Linguagem
            if "typescript" in deps_keys or (inspect_dir / "tsconfig.json").exists() or (directory / "tsconfig.json").exists():
                primary_language = "TypeScript"
                languages.extend(["TypeScript", "JavaScript"])
            else:
                primary_language = "JavaScript"
                languages.append("JavaScript")

            # Gerenciador de pacotes
            if (directory / "bun.lock").exists() or (inspect_dir / "bun.lock").exists():
                package_manager = "bun"
            elif (directory / "pnpm-lock.yaml").exists() or (inspect_dir / "pnpm-lock.yaml").exists():
                package_manager = "pnpm"
            elif (directory / "yarn.lock").exists() or (inspect_dir / "yarn.lock").exists():
                package_manager = "yarn"
            else:
                package_manager = "npm"

            # Frameworks e Ferramentas
            # React
            if "react" in deps_keys or "@vitejs/plugin-react" in deps_keys or "react" in raw_lower:
                react_ver = str(all_deps.get("react", ""))
                if "19" in react_ver or "^19" in react_ver:
                    frameworks.append("React 19")
                    frameworks.append("React")
                else:
                    frameworks.append("React")

            # Vite
            if "vite" in deps_keys or "@vitejs/plugin-react" in deps_keys or (inspect_dir / "vite.config.ts").exists() or (inspect_dir / "vite.config.js").exists() or "vite" in raw_lower:
                frameworks.append("Vite")

            # Tailwind CSS
            if (
                "tailwindcss" in deps_keys
                or "@tailwindcss/vite" in deps_keys
                or "@tailwindcss/postcss" in deps_keys
                or (inspect_dir / "tailwind.config.js").exists()
                or (inspect_dir / "tailwind.config.ts").exists()
                or "tailwind" in raw_lower
            ):
                frameworks.append("Tailwind CSS")

            # Express
            if "express" in deps_keys or "@types/express" in deps_keys:
                frameworks.append("Express")

            # Firebase
            if "firebase" in deps_keys or "firebase-admin" in deps_keys or (directory / "firestore.rules").exists():
                frameworks.append("Firebase")

            # Google GenAI
            if "@google/genai" in deps_keys or "@google/generative-ai" in deps_keys:
                frameworks.append("Google GenAI")

            # Outros frameworks conhecidos
            if "@xyflow/react" in deps_keys:
                frameworks.append("XYFlow")
            if "next" in deps_keys:
                frameworks.append("Next.js")
            if "remix" in deps_keys or "@remix-run/react" in deps_keys:
                frameworks.append("Remix")

            # Comando de Dev
            if "dev" in scripts:
                rel_app = inspect_dir.relative_to(directory).as_posix() if inspect_dir != directory else ""
                if rel_app:
                    dev_command = f"{package_manager} run dev ({rel_app})"
                else:
                    dev_command = f"{package_manager} run dev"
            elif "start" in scripts:
                dev_command = f"{package_manager} start"

            # Tentar extrair porta configurada no script dev
            dev_script_str = str(scripts.get("dev", ""))
            port_match = re.search(r"--port\s+(\d+)", dev_script_str)
            if port_match:
                default_port = int(port_match.group(1))

        # 2. Inspeção de pyproject.toml ou requirements.txt (Python)
        pyproj_file = inspect_dir / "pyproject.toml"
        req_file = inspect_dir / "requirements.txt"
        if pyproj_file.exists() or req_file.exists():
            if not manifest_type:
                manifest_type = "pyproject.toml" if pyproj_file.exists() else "requirements.txt"
                primary_language = "Python"
                languages.append("Python")

            py_deps: list[str] = []
            if pyproj_file.exists():
                try:
                    py_data = tomllib.loads(pyproj_file.read_text(encoding="utf-8"))
                    proj_sec = py_data.get("project", {})
                    package_name = package_name or proj_sec.get("name")
                    py_deps.extend(proj_sec.get("dependencies", []))
                    opt_deps = proj_sec.get("optional-dependencies", {})
                    for group_deps in opt_deps.values():
                        if isinstance(group_deps, list):
                            py_deps.extend(group_deps)
                    manifests.append(
                        ManifestInfo(
                            manifest_type="pyproject.toml",
                            path=pyproj_file,
                            package_name=package_name,
                            version=proj_sec.get("version"),
                            dependencies=py_deps,
                        )
                    )
                except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError) as err:
                    logger.debug("Falha ao ler pyproject.toml em %s: %s", pyproj_file, err)

            if req_file.exists():
                try:
                    lines = [l.strip() for l in req_file.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
                    py_deps.extend(lines)
                except (OSError, UnicodeDecodeError) as err:
                    logger.debug("Falha ao ler requirements.txt em %s: %s", req_file, err)

            deps_lower = [d.lower() for d in py_deps]
            all_py_str = " ".join(deps_lower)

            if "fastapi" in all_py_str:
                frameworks.append("FastAPI")
            if "playwright" in all_py_str:
                frameworks.append("Playwright")
            if "pydantic" in all_py_str:
                frameworks.append("Pydantic")
            if "pytest" in all_py_str:
                frameworks.append("Pytest")
            if "beautifulsoup4" in all_py_str or "bs4" in all_py_str:
                frameworks.append("BeautifulSoup4")
            if "httpx" in all_py_str:
                frameworks.append("HTTPX")
            if "rich" in all_py_str:
                frameworks.append("Rich")
            if "pyspark" in all_py_str:
                frameworks.append("PySpark")
            if "streamlit" in all_py_str:
                frameworks.append("Streamlit")
            if "flask" in all_py_str:
                frameworks.append("Flask")

            if (directory / "uv.lock").exists() or (inspect_dir / "uv.lock").exists():
                package_manager = package_manager or "uv"
            elif (directory / "poetry.lock").exists():
                package_manager = package_manager or "poetry"
            else:
                package_manager = package_manager or "pip"

            if not dev_command:
                if "pytest" in frameworks:
                    dev_command = "uv run pytest"
                else:
                    dev_command = "python main.py"

        # 3. Inspeção de go.mod (Go)
        go_mod = inspect_dir / "go.mod"
        if go_mod.exists():
            manifest_type = manifest_type or "go.mod"
            primary_language = "Go"
            languages.append("Go")
            package_manager = "go"
            dev_command = dev_command or "go run ."

            try:
                content = go_mod.read_text(encoding="utf-8")
                lines = content.splitlines()
                for line in lines:
                    line_s = line.strip()
                    if line_s.startswith("module "):
                        package_name = package_name or line_s.split()[1]
                if "google.golang.org/adk" in content:
                    frameworks.append("Google ADK")
                if "google.golang.org/genai" in content:
                    frameworks.append("Google GenAI")
                if "github.com/gorilla/mux" in content:
                    frameworks.append("Gorilla Mux")
                if "github.com/gin-gonic/gin" in content:
                    frameworks.append("Gin")

                manifests.append(
                    ManifestInfo(
                        manifest_type="go.mod",
                        path=go_mod,
                        package_name=package_name,
                    )
                )
            except (OSError, UnicodeDecodeError) as err:
                logger.debug("Falha ao ler go.mod em %s: %s", go_mod, err)

        # Deduplicar frameworks mantendo a ordem
        unique_frameworks: list[str] = []
        for fw in frameworks:
            if fw not in unique_frameworks:
                unique_frameworks.append(fw)

        return StackDetails(
            primary_language=primary_language,
            languages=languages,
            frameworks=unique_frameworks,
            manifest_type=manifest_type,
            package_name=package_name,
            dev_command=dev_command,
            package_manager=package_manager,
            default_port=default_port,
            manifests=manifests,
        )

    @classmethod
    def list_all_projects(
        cls,
        include_system: bool = False,
        workspace_root: Path | None = None,
    ) -> list[ProjectTargetInfo]:
        """Lista todos os projetos canônicos consolidados a partir de projects.json e do sistema de arquivos."""
        root = workspace_root or Path(__file__).resolve().parents[1]
        signature = cls._registry_signature(root)
        cache_key = (str(root.resolve()), include_system, signature)
        cached = cls._projects_cache.get(cache_key)
        if cached is not None:
            return [project.model_copy(deep=True) for project in cached]
        local_projects_dir = root / "projects"

        # Mapa consolidado por chave canônica
        projects_map: dict[str, ProjectTargetInfo] = {}

        # 1. Carregar a SSoT canônica C:\Users\melki\.gemini\projects.json
        if cls.CANONICAL_PROJECTS_JSON.exists():
            try:
                data = json.loads(cls.CANONICAL_PROJECTS_JSON.read_text(encoding="utf-8"))
                registered = data.get("projects", {})
                for raw_path, slug in registered.items():
                    norm_path = Path(raw_path).resolve()
                    slug_clean = str(slug).strip()

                    # Classificação da categoria
                    category = "client_project"
                    path_str_lower = norm_path.as_posix().lower()
                    slug_lower = slug_clean.lower()
                    if (
                        "system32" in path_str_lower
                        or "appdata" in path_str_lower
                        or "scratch" in path_str_lower
                        or ".gemini" in path_str_lower
                        or path_str_lower.endswith("/brain")
                        or path_str_lower == "c:/users/melki"
                        or path_str_lower == "c:/users/melki/projetos"
                        or slug_lower in ("scratch", "melki", "antigravity-ide", "scratch-1", "antigravity-ide-1", "brain", "system32", "projetos")
                    ):
                        category = "system"
                        if not include_system:
                            continue
                    elif "meu-workspace-global" in path_str_lower:
                        category = "workspace"
                    elif "wise-galileo" in path_str_lower:
                        category = "knowledge_base"
                    elif "mdk-teste" in path_str_lower:
                        category = "internal_tool"

                    # Verificar existência de junction local em projects/
                    junction_path: Path | None = None
                    is_junction = False
                    if local_projects_dir.exists():
                        for cand in [local_projects_dir / slug_clean, local_projects_dir / norm_path.name]:
                            if cand.exists() and is_ntfs_junction(cand):
                                junction_path = cand
                                is_junction = True
                                break

                    meta = KNOWN_METADATA.get(slug_clean, KNOWN_METADATA.get(norm_path.name, {}))
                    subpath = meta.get("subpath")
                    inspect_path = (norm_path / subpath) if subpath and (norm_path / subpath).exists() else norm_path
                    stack = cls.detect_stack(inspect_path) if norm_path.exists() else StackDetails()
                    tech_stack = cls._extract_tech_stack_tags(stack)
                    port = meta.get("port", stack.default_port)
                    env_file_exists = (inspect_path / ".env").exists() if norm_path.exists() else False

                    display_name = meta.get("display_name", slug_clean)
                    aliases = list(meta.get("aliases", [slug_clean]))
                    if slug_clean not in aliases:
                        aliases.append(slug_clean)
                    if norm_path.name not in aliases:
                        aliases.append(norm_path.name)

                    info = ProjectTargetInfo(
                        key=slug_clean,
                        name=norm_path.name if norm_path.exists() else slug_clean,
                        display_name=display_name,
                        canonical_path=norm_path,
                        target_path=norm_path,
                        junction_path=junction_path,
                        local_junction_path=junction_path,
                        is_junction=is_junction,
                        exists=norm_path.exists(),
                        subpath=subpath,
                        stack=stack,
                        stack_details=stack,
                        tech_stack=tech_stack,
                        port=port,
                        env_file_exists=env_file_exists,
                        category=category,
                        description=f"Projeto {display_name} localizado em {norm_path.as_posix()}",
                        aliases=aliases,
                    )
                    projects_map[slug_clean] = info
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as err:
                logger.debug("Falha ao processar projects.json canônico: %s", err)

        # 2. Descoberta complementar em C:\Users\melki\Projetos (ex: tactile-ui-studio)
        if cls.CANONICAL_EXTERNAL_PROJECTS_DIR.exists():
            for child in cls.CANONICAL_EXTERNAL_PROJECTS_DIR.iterdir():
                if child.is_dir() and not child.name.startswith("."):
                    key = child.name
                    # Normalizar canvas_ide vs canvas-ide
                    key_matched = None
                    for existing_key in projects_map:
                        if existing_key.lower() == key.lower() or existing_key.replace("-", "_") == key.replace("-", "_"):
                            key_matched = existing_key
                            break

                    if not key_matched:
                        meta = KNOWN_METADATA.get(key, {})
                        subpath = meta.get("subpath")
                        inspect_path = (child / subpath) if subpath and (child / subpath).exists() else child
                        stack = cls.detect_stack(inspect_path)
                        tech_stack = cls._extract_tech_stack_tags(stack)
                        port = meta.get("port", stack.default_port)
                        env_file_exists = (inspect_path / ".env").exists()
                        display_name = meta.get("display_name", key)
                        aliases = list(meta.get("aliases", [key]))

                        local_junc = local_projects_dir / key
                        if not local_junc.exists() and key in KNOWN_METADATA:
                            for a in KNOWN_METADATA[key].get("aliases", []):
                                cand_junc = local_projects_dir / a
                                if cand_junc.exists():
                                    local_junc = cand_junc
                                    break
                        junc_found = local_junc if local_junc.exists() and is_ntfs_junction(local_junc) else None

                        info = ProjectTargetInfo(
                            key=key,
                            name=key,
                            display_name=display_name,
                            canonical_path=child.resolve(),
                            target_path=child.resolve(),
                            junction_path=junc_found,
                            local_junction_path=junc_found,
                            is_junction=False,
                            exists=True,
                            subpath=subpath,
                            stack=stack,
                            stack_details=stack,
                            tech_stack=tech_stack,
                            port=port,
                            env_file_exists=env_file_exists,
                            category="client_project",
                            description=f"Projeto cliente descoberto em {child.as_posix()}",
                            aliases=aliases,
                        )
                        projects_map[key] = info

        # 3. Descoberta complementar de ferramentas locais em meu-workspace-global/projects
        if local_projects_dir.exists():
            for child in local_projects_dir.iterdir():
                if child.is_dir() and not is_ntfs_junction(child) and not child.name.startswith("."):
                    key = child.name
                    if key not in projects_map or workspace_root is not None:
                        meta = KNOWN_METADATA.get(key, {})
                        stack = cls.detect_stack(child)
                        tech_stack = cls._extract_tech_stack_tags(stack)
                        aliases = list(meta.get("aliases", [key]))
                        if key not in aliases:
                            aliases.append(key)
                        info = ProjectTargetInfo(
                            key=key,
                            name=key,
                            display_name=meta.get("display_name", key),
                            canonical_path=child.resolve(),
                            target_path=child.resolve(),
                            junction_path=child.resolve(),
                            local_junction_path=child.resolve(),
                            is_junction=False,
                            exists=True,
                            stack=stack,
                            stack_details=stack,
                            tech_stack=tech_stack,
                            port=meta.get("port", stack.default_port),
                            env_file_exists=(child / ".env").exists(),
                            category=meta.get("category", "internal_tool"),
                            description=f"Ferramenta interna em {child.as_posix()}",
                            aliases=aliases,
                        )
                        projects_map[key] = info

        # 4. Registrar pacotes Go internos conhecidos (ex: customer_issue_reviewer_go)
        go_tool_dir = root / "agents" / "specialized" / "customer_issue_reviewer_go"
        if go_tool_dir.exists() and "customer_issue_reviewer_go" not in projects_map:
            meta = KNOWN_METADATA.get("customer_issue_reviewer_go", {})
            stack = cls.detect_stack(go_tool_dir)
            tech_stack = cls._extract_tech_stack_tags(stack)
            projects_map["customer_issue_reviewer_go"] = ProjectTargetInfo(
                key="customer_issue_reviewer_go",
                name="customer_issue_reviewer_go",
                display_name=meta.get("display_name", "Customer Issue Reviewer (Go)"),
                canonical_path=go_tool_dir.resolve(),
                target_path=go_tool_dir.resolve(),
                exists=True,
                stack=stack,
                stack_details=stack,
                tech_stack=tech_stack,
                category="internal_tool",
                description=f"Agente especializado Go em {go_tool_dir.as_posix()}",
                aliases=meta.get("aliases", ["customer_issue_reviewer_go"]),
            )

        projects = list(projects_map.values())
        cls._projects_cache = {
            key: value for key, value in cls._projects_cache.items()
            if key[0] != str(root.resolve()) or key[1] != include_system
        }
        cls._projects_cache[cache_key] = [project.model_copy(deep=True) for project in projects]
        return projects

    @classmethod
    def get_project(cls, name_or_alias: str | Path, workspace_root: Path | None = None) -> ProjectTargetInfo | None:
        """Busca determinística direta por nome, chave canônica, alias registrado ou caminho de junction/diretório."""
        query_str = str(name_or_alias).strip()
        query_lower = query_str.lower()
        projects = cls.list_all_projects(include_system=True, workspace_root=workspace_root)
        root = workspace_root or Path(__file__).resolve().parents[1]

        # 0. Busca por caminho direto ou desreferenciação de junction no sistema de arquivos
        cand_path = Path(query_str)
        cands_to_check: list[Path] = []
        if cand_path.is_absolute() and cand_path.exists() or cand_path.exists():
            cands_to_check.append(cand_path.resolve())
        if (root / query_str).exists():
            cands_to_check.append((root / query_str).resolve())
        if (root / "projects" / query_str).exists():
            cands_to_check.append((root / "projects" / query_str).resolve())

        for cpath in cands_to_check:
            for p in projects:
                if p.local_junction_path and p.local_junction_path.exists() and (p.local_junction_path == cand_path or p.local_junction_path.resolve() == cpath):
                    p_copy = p.model_copy()
                    p_copy.is_junction = True
                    p_copy.target_path = p.local_junction_path
                    return p_copy
                if p.canonical_path.resolve() == cpath:
                    return p

        # 1. Busca exata por chave ou nome
        for p in projects:
            if p.key.lower() == query_lower or p.name.lower() == query_lower:
                return p

        # 2. Busca por alias
        for p in projects:
            aliases_lower = [a.lower() for a in p.aliases]
            if query_lower in aliases_lower:
                return p

        # 3. Busca por correspondência de caminhos ou pastas
        for p in projects:
            if p.canonical_path.name.lower() == query_lower:
                return p

        return None

    @classmethod
    def resolve_target(cls, user_input: str, workspace_root: Path | None = None) -> ProjectTargetInfo | None:
        """Resolve menções casuais ou explícitas em linguagem natural para um projeto canônico."""
        text_lower = user_input.lower()
        projects = cls.list_all_projects(include_system=False, workspace_root=workspace_root)

        # Mapear todos os aliases conhecidos com prioridade para os mais longos
        alias_to_project: list[tuple[str, ProjectTargetInfo]] = []
        for p in projects:
            for alias in p.aliases:
                alias_to_project.append((alias.lower(), p))
            alias_to_project.append((p.key.lower(), p))
            alias_to_project.append((p.name.lower(), p))

        # Adicionar aliases legados de KNOWN_PROJECT_NAMES
        for alias, folder_name in KNOWN_PROJECT_NAMES.items():
            proj = cls.get_project(folder_name, workspace_root=workspace_root)
            if proj:
                alias_to_project.append((alias.lower(), proj))

        # Ordenar decrescente pelo comprimento do alias para dar precedência a termos mais específicos
        alias_to_project.sort(key=lambda x: len(x[0]), reverse=True)

        for alias, proj in alias_to_project:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, text_lower):
                return proj

        # Fallback de correspondência dinâmica com pastas de projetos
        root = workspace_root or Path(__file__).resolve().parents[1]
        search_dirs = [cls.CANONICAL_EXTERNAL_PROJECTS_DIR, root / "projects"]
        for pdir in search_dirs:
            if pdir.exists():
                for child in pdir.iterdir():
                    if (child.is_dir() or is_ntfs_junction(child)) and child.name.lower() in text_lower:
                        resolved = cls.get_project(child.name, workspace_root=workspace_root)
                        if resolved:
                            return resolved

        return None

    @classmethod
    def resolve_project(cls, identifier: str, workspace_root: Path | None = None) -> ProjectTargetInfo:
        """Resolve um identificador para ProjectTargetInfo garantindo retorno tipado."""
        found = cls.get_project(identifier, workspace_root=workspace_root)
        if found:
            return found

        target = cls.resolve_target(identifier, workspace_root=workspace_root)
        if target:
            return target

        # Caso não exista, retorna estrutura consistente com exists=False
        fake_path = cls.CANONICAL_EXTERNAL_PROJECTS_DIR / identifier
        return ProjectTargetInfo(
            key=identifier,
            name=identifier,
            display_name=identifier,
            canonical_path=fake_path,
            target_path=fake_path,
            exists=False,
            description=f"Projeto '{identifier}' não encontrado no ecossistema.",
        )

    @classmethod
    def scan_directory(cls, directory: Path, max_depth: int = 3) -> dict[str, Any]:
        """Varre recursivamente o diretório com limites e substitui a lógica de WorkspaceSpecialistAgent."""
        scan_dir = directory.resolve() if directory.exists() else directory
        file_tree: list[str] = []
        stack_details = cls.detect_stack(scan_dir)
        tech_stack = cls._extract_tech_stack_tags(stack_details)

        if scan_dir.exists() and scan_dir.is_dir():
            try:
                for path in scan_dir.rglob("*"):
                    # Ignorar diretórios pesados e temporários
                    if any(part in path.parts for part in [".venv", "node_modules", "__pycache__", ".git", "dist", ".brain", "artifacts"]):
                        continue
                    try:
                        rel_path = path.relative_to(scan_dir)
                    except ValueError:
                        rel_path = path

                    if len(rel_path.parts) <= max_depth:
                        icon = "📁" if path.is_dir() else "📄"
                        file_tree.append(f"{icon} {rel_path.as_posix()}")
            except OSError:
                pass

        return {
            "agent": "ProjectTargetResolver",
            "root_path": scan_dir.as_posix(),
            "is_target_project": True,
            "tech_stack": tech_stack,
            "stack_details": stack_details.model_dump(),
            "total_items_scanned": len(file_tree),
            "files": file_tree,
            "tree_preview": file_tree[:30],
            "status": "success",
        }


if __name__ == "__main__":
    import sys

    if "--json" in sys.argv:
        all_projs = [p.to_dict() for p in ProjectTargetResolver.list_all_projects()]
        print(json.dumps({"projects": all_projs}, indent=2, ensure_ascii=False))
    elif "--list" in sys.argv:
        projs = ProjectTargetResolver.list_all_projects()
        print(f"\nProjetos registrados no ecossistema ({len(projs)}):")
        for p in projs:
            junc_str = " (Junction)" if p.is_junction else ""
            port_str = f"[:{p.port}]" if p.port else ""
            print(f"  • [{p.key}] {p.display_name} {port_str}{junc_str} -> {p.canonical_path.as_posix()}")
    elif len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        resolved = ProjectTargetResolver.resolve_target(query)
        if resolved:
            print(f"Resolvido: [{resolved.key}] {resolved.display_name} -> {resolved.canonical_path.as_posix()}")
            print(f"Stack: {resolved.tech_stack}")
        else:
            print(f"Nenhum projeto encontrado para: '{query}'")
