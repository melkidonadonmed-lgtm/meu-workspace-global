"""Testes do ProjectTargetResolver (resolução determinística de projetos-alvo em projects/)."""

from pathlib import Path

from pydantic import BaseModel

from agents.project_resolver import (
    ManifestInfo,
    ProjectTargetInfo,
    ProjectTargetResolver,
    StackDetails,
)

WORKSPACE_DIR = Path(__file__).resolve().parents[2]


def _create_workspace_projects(tmp_path: Path) -> Path:
    projects_dir = tmp_path / "projects"
    (projects_dir / "pcm").mkdir(parents=True)
    (projects_dir / "canvas_ide").mkdir(parents=True)
    (projects_dir / "keepdocs-workspace").mkdir(parents=True)
    (projects_dir / "mdk").mkdir(parents=True)
    (projects_dir / "pcm" / "package.json").write_text(
        '{"dependencies":{"react":"18.0.0","vite":"5.0.0"}}',
        encoding="utf-8",
    )
    (projects_dir / "mdk" / "package.json").write_text(
        '{"dependencies":{"next":"14.2.5","react":"18.3.1"}}',
        encoding="utf-8",
    )
    return tmp_path


def test_target_project_resolver_prioritizes_workspace(tmp_path: Path):
    """Valida que mencoes a 'pcm' resolvem para projects/pcm dentro do workspace."""
    resolver = ProjectTargetResolver()
    workspace_dir = _create_workspace_projects(tmp_path)
    info = resolver.resolve_target("audite a interface do projeto pcm para criancas", workspace_dir)
    assert info is not None
    assert info.name == "pcm"
    assert info.exists
    assert info.target_path == workspace_dir / "projects" / "pcm"
    assert "React" in info.tech_stack
    assert "Vite" in info.tech_stack


def test_target_project_resolver_canvas_and_keepdocs(tmp_path: Path):
    """Valida redirecionamento canônico de canvas_ide e keepdocs-workspace para mdk."""
    resolver = ProjectTargetResolver()
    workspace_dir = _create_workspace_projects(tmp_path)

    info_canvas = resolver.resolve_target("reorganize o layout no canvas_ide", workspace_dir)
    assert info_canvas is not None
    assert info_canvas.name == "mdk"
    assert info_canvas.exists
    assert info_canvas.target_path == workspace_dir / "projects" / "mdk"

    info_keepdocs = resolver.resolve_target("atualize a documentacao no keepdocs-workspace", workspace_dir)
    assert info_keepdocs is not None
    assert info_keepdocs.name == "mdk"
    assert info_keepdocs.exists
    assert info_keepdocs.target_path == workspace_dir / "projects" / "mdk"


def test_target_project_resolver_returns_none_for_unknown():
    """Sem projeto reconhecível na frase, retorna None em vez de adivinhar."""
    resolver = ProjectTargetResolver()
    assert resolver.resolve_target("oi, tudo bem?", WORKSPACE_DIR) is None


def test_list_all_projects_loads_projects_json():
    """Valida carregamento dinâmico e resolução da SSoT projects.json."""
    projects = ProjectTargetResolver.list_all_projects()
    assert len(projects) >= 9
    keys = [p.key.lower() for p in projects]
    assert "pcm" in keys
    assert "mdk" in keys
    assert "waoe" in keys
    assert "tactile-ui-studio" in keys


def test_list_all_projects_reuses_cached_registry(tmp_path: Path, monkeypatch):
    """Garante que resoluções repetidas não reanalisam todos os projetos."""
    workspace_dir = _create_workspace_projects(tmp_path)
    ProjectTargetResolver.clear_cache()
    calls = 0
    original_detect_stack = ProjectTargetResolver.detect_stack

    def counting_detect_stack(directory: Path) -> StackDetails:
        nonlocal calls
        calls += 1
        return original_detect_stack(directory)

    monkeypatch.setattr(ProjectTargetResolver, "detect_stack", counting_detect_stack)

    first = ProjectTargetResolver.list_all_projects(workspace_root=workspace_dir)
    calls_after_first = calls
    second = ProjectTargetResolver.list_all_projects(workspace_root=workspace_dir)

    assert first
    assert second
    assert calls_after_first > 0
    assert calls == calls_after_first


def test_deep_stack_detection_react_vite():
    """Valida detecção rica de dependências para pcm e canvas_ide."""
    pcm = ProjectTargetResolver.get_project("pcm")
    assert pcm is not None
    assert pcm.exists
    assert "React" in pcm.tech_stack
    assert "Vite" in pcm.tech_stack
    assert pcm.port == 3000


def test_deep_stack_detection_tactile_monorepo():
    """Valida detecção profunda em subpastas de monorepos (apps/atlas-ui-kit)."""
    tactile = ProjectTargetResolver.get_project("tactile-ui-studio")
    assert tactile is not None
    assert tactile.exists
    assert "React" in tactile.tech_stack
    assert "Vite" in tactile.tech_stack
    assert tactile.port == 4173


def test_deep_stack_detection_python():
    """Valida detecção rica de Python e dependências."""
    auditor = ProjectTargetResolver.get_project("web_visual_auditor")
    if auditor and auditor.exists:
        assert "Python" in auditor.tech_stack


def test_deep_stack_detection_go():
    """Valida detecção de Go e Google ADK."""
    go_proj = ProjectTargetResolver.get_project("customer_issue_reviewer_go")
    if go_proj and go_proj.exists:
        assert "Go" in go_proj.tech_stack


def test_workspace_specialist_delegation():
    """Valida que WorkspaceSpecialistAgent delega para ProjectTargetResolver sem duplicar código."""
    from agents.specialized.workspace_specialist import WorkspaceSpecialistAgent

    agent = WorkspaceSpecialistAgent(str(WORKSPACE_DIR))
    res = agent.scan_workspace("projects/pcm", max_depth=2)
    assert res.get("status") == "success"
    assert "React" in res.get("tech_stack", [])


def test_resolve_project_typed_contract_and_pydantic_instance():
    """Valida conformidade estrita com o contrato de interface Pydantic BaseModel."""
    info = ProjectTargetResolver.resolve_project("pcm")
    assert isinstance(info, BaseModel)
    assert isinstance(info, ProjectTargetInfo)
    assert info.key == "pcm"
    assert info.exists is True
    assert info.canonical_path.is_absolute()
    assert isinstance(info.stack, StackDetails)
    assert isinstance(info.stack, BaseModel)
    assert info.port == 3000

    # Validação do dump tipado
    dumped = info.model_dump()
    assert isinstance(dumped, dict)
    assert dumped["key"] == "pcm"
    assert dumped["port"] == 3000

    stack_dump = info.stack.model_dump()
    assert "primary_language" in stack_dump
    assert "frameworks" in stack_dump


def test_resolve_project_nonexistent_returns_typed_info_exists_false():
    """Valida que identificadores não cadastrados retornam ProjectTargetInfo com exists=False."""
    fake_key = "projeto_fantasma_xyz_999"
    info = ProjectTargetResolver.resolve_project(fake_key)
    assert isinstance(info, ProjectTargetInfo)
    assert info.exists is False
    assert info.key == fake_key
    assert info.port is None
    assert info.is_junction is False


def test_resolve_project_by_junction_path_bidirectional():
    """Valida resolução determinística bidirecional quando informado o caminho de junction."""
    junction_target = WORKSPACE_DIR / "projects" / "pcm"
    info = ProjectTargetResolver.get_project(junction_target)
    assert info is not None
    assert info.key == "pcm"
    assert info.exists is True
    assert info.is_junction is True
    assert info.local_junction_path is not None


def test_resolve_aliases_comprehensive():
    """Valida resolução para ampla gama de aliases canônicos conhecidos."""
    pcm_aliases = ["prescmed", "prescmed-v2", "prescmed-pcm", "pcm"]
    for alias in pcm_aliases:
        p = ProjectTargetResolver.get_project(alias)
        assert p is not None, f"Falha ao resolver alias: {alias}"
        assert p.key == "pcm"

    mdk_and_canvas_aliases = ["mdk", "mdk-cockpit", "canvas_ide", "canvas-ide", "canvas"]
    for alias in mdk_and_canvas_aliases:
        p = ProjectTargetResolver.get_project(alias)
        assert p is not None, f"Falha ao resolver alias: {alias}"
        assert p.key == "mdk"

    tactile_aliases = ["tactile-ui-studio", "tactile", "atlas-ui-kit"]
    for alias in tactile_aliases:
        p = ProjectTargetResolver.get_project(alias)
        assert p is not None, f"Falha ao resolver alias: {alias}"
        assert p.key == "tactile-ui-studio"


def test_detect_stack_handles_empty_or_nonexistent_directory():
    """Valida resiliência de detecção para diretórios inexistentes ou vazios."""
    fake_dir = WORKSPACE_DIR / "non_existent_folder_abc"
    details = ProjectTargetResolver.detect_stack(fake_dir)
    assert isinstance(details, StackDetails)
    assert details.primary_language == "Unknown"
    assert details.frameworks == []
    assert details.manifest_type == ""
    assert details.dev_command is None


def test_scan_directory_filters_heavy_folders():
    """Valida que a varredura respeita limites de profundidade e exclui pastas pesadas."""
    pcm_proj = WORKSPACE_DIR / "projects" / "pcm"
    res = ProjectTargetResolver.scan_directory(pcm_proj, max_depth=2)
    assert res.get("status") == "success"
    assert res.get("is_target_project") is True
    files = res.get("files", [])
    for f in files:
        assert not f.startswith("📁 node_modules")
        assert not f.startswith("📁 .git/")
        assert not f.startswith("📁 .venv")


def test_ssot_projects_json_canonical_path_normalization():
    """Valida que a SSoT projects.json é consumida com caminhos resolvidos e normalizados."""
    assert ProjectTargetResolver.CANONICAL_PROJECTS_JSON.exists()
    projects = ProjectTargetResolver.list_all_projects(include_system=True)
    for p in projects:
        assert p.canonical_path.is_absolute()
        assert isinstance(p.canonical_path, Path)


def test_manifest_info_extraction_deep():
    """Valida extração rica e detalhada dos manifests de dependências."""
    pcm = ProjectTargetResolver.get_project("pcm")
    assert pcm is not None
    assert pcm.stack.manifests
    first_manifest = pcm.stack.manifests[0]
    assert isinstance(first_manifest, ManifestInfo)
    assert first_manifest.manifest_type == "package.json"
    assert "react" in [d.lower() for d in first_manifest.dependencies]
    assert "vite" in [d.lower() for d in first_manifest.dev_dependencies]
