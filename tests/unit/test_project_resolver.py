"""Testes do ProjectTargetResolver (resolução determinística de projetos-alvo em projects/)."""

from pathlib import Path

from agents.project_resolver import ProjectTargetResolver


def _create_workspace_projects(tmp_path: Path) -> Path:
    projects_dir = tmp_path / "projects"
    (projects_dir / "pcm").mkdir(parents=True)
    (projects_dir / "canvas_ide").mkdir(parents=True)
    (projects_dir / "keepdocs-workspace").mkdir(parents=True)
    (projects_dir / "pcm" / "package.json").write_text(
        '{"dependencies":{"react":"18.0.0","vite":"5.0.0"}}',
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
    """Valida deteccao correta de canvas_ide e keepdocs-workspace."""
    resolver = ProjectTargetResolver()
    workspace_dir = _create_workspace_projects(tmp_path)

    info_canvas = resolver.resolve_target("reorganize o layout no canvas_ide", workspace_dir)
    assert info_canvas is not None
    assert info_canvas.name == "canvas_ide"
    assert info_canvas.exists
    assert info_canvas.target_path == workspace_dir / "projects" / "canvas_ide"

    info_keepdocs = resolver.resolve_target("atualize a documentacao no keepdocs-workspace", workspace_dir)
    assert info_keepdocs is not None
    assert info_keepdocs.name == "keepdocs-workspace"
    assert info_keepdocs.exists
    assert info_keepdocs.target_path == workspace_dir / "projects" / "keepdocs-workspace"


def test_target_project_resolver_returns_none_for_unknown():
    """Sem projeto reconhecível na frase, retorna None em vez de adivinhar."""
    resolver = ProjectTargetResolver()
    assert resolver.resolve_target("oi, tudo bem?", Path(__file__).resolve().parents[2]) is None
