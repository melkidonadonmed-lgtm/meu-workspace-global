"""Testes do ProjectTargetResolver (resolução determinística de projetos-alvo em projects/)."""

from pathlib import Path

from agents.project_resolver import ProjectTargetResolver

WORKSPACE_DIR = Path(__file__).resolve().parents[2]


def _create_project(workspace_dir: Path, name: str, package_json: str | None = None) -> None:
    project_dir = workspace_dir / "projects" / name
    project_dir.mkdir(parents=True, exist_ok=True)
    if package_json is not None:
        (project_dir / "package.json").write_text(package_json, encoding="utf-8")


def test_target_project_resolver_prioritizes_workspace(tmp_path: Path):
    """Valida que mencoes a 'pcm' resolvem para projects/pcm dentro do workspace."""
    _create_project(
        tmp_path,
        "pcm",
        '{"dependencies":{"react":"18.0.0"},"devDependencies":{"vite":"5.0.0","typescript":"5.0.0"}}',
    )
    resolver = ProjectTargetResolver()
    info = resolver.resolve_target("audite a interface do projeto pcm para criancas", tmp_path)
    assert info is not None
    assert info.name == "pcm"
    assert info.exists
    assert "pcm" in info.target_path.as_posix().lower()
    assert "React" in info.tech_stack
    assert "Vite" in info.tech_stack


def test_target_project_resolver_canvas_and_keepdocs(tmp_path: Path):
    """Valida deteccao correta de canvas_ide e keepdocs-workspace."""
    _create_project(tmp_path, "canvas_ide")
    _create_project(tmp_path, "keepdocs-workspace")
    resolver = ProjectTargetResolver()

    info_canvas = resolver.resolve_target("reorganize o layout no canvas_ide", tmp_path)
    assert info_canvas is not None
    assert info_canvas.name == "canvas_ide"
    assert info_canvas.exists

    info_keepdocs = resolver.resolve_target("atualize a documentacao no keepdocs-workspace", tmp_path)
    assert info_keepdocs is not None
    assert info_keepdocs.name == "keepdocs-workspace"
    assert info_keepdocs.exists


def test_target_project_resolver_returns_none_for_unknown():
    """Sem projeto reconhecível na frase, retorna None em vez de adivinhar."""
    resolver = ProjectTargetResolver()
    assert resolver.resolve_target("oi, tudo bem?", WORKSPACE_DIR) is None
