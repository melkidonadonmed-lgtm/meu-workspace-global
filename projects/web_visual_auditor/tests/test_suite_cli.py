"""Testes automatizados e determinísticos para WebVisualAuditorSuite e CLI (Milestone M5).

Cobertura completa de:
1. Métodos individuais da classe WebVisualAuditorSuite (pesquisa, higienização, DOM, diff visual e componentes).
2. Pipeline consolidado run_full_suite com validação de status PASS/FAIL e métricas agregadas.
3. Subcomandos oficiais da CLI (search, dom-inspect, visual-diff, component-diff, suite) via main().
4. Formatação de saídas em texto amigável e JSON.
5. Códigos de saída POSIX (0 = sucesso/sem divergência, 1 = divergência/erro, 2 = erro de sintaxe).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from PIL import Image

from web_visual_auditor.cli import build_parser, main
from web_visual_auditor.dom_auditor import DOMAuditor
from web_visual_auditor.models import (
    ComponentDiffReport,
    DOMNodeSummary,
    SourceReference,
    SuiteAuditReport,
    VisualDiffResult,
)
from web_visual_auditor.researcher import WebResearcher
from web_visual_auditor.suite import SuiteConfig, WebVisualAuditorSuite
from web_visual_auditor.visual_regression import VisualRegressionAuditor

# =============================================================================
# Fixtures Locais e Determinísticas
# =============================================================================


@pytest.fixture
def sample_html_content() -> str:
    """Retorna código HTML representativo contendo elementos-chave e nós ruidosos."""
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Página de Demonstração de Auditoria</title>
    <style>body { font-family: sans-serif; } .hidden { display: none; }</style>
    <script>console.log("Ruído de telemetria");</script>
</head>
<body>
    <header id="site-header" class="main-header">
        <h1>Título Principal do Header</h1>
        <nav id="site-nav">
            <a href="/inicio">Início</a>
            <a href="/artigos">Artigos</a>
        </nav>
    </header>
    <main id="content-area">
        <article id="featured-article">
            <h2>Artigo em Destaque</h2>
            <p>Este é o conteúdo do primeiro parágrafo de teste informativo.</p>
            <svg><circle cx="50" cy="50" r="40" /></svg>
        </article>
        <button id="primary-action-btn" class="btn-primary" style="width: 150px; height: 40px;">
            Confirmar Ação
        </button>
        <div id="hidden-box" class="hidden">Elemento oculto</div>
    </main>
    <footer id="site-footer">
        <p>Rodapé corporativo</p>
    </footer>
</body>
</html>"""


@pytest.fixture
def sample_html_file(tmp_path: Path, sample_html_content: str) -> Path:
    """Cria um arquivo HTML temporário no disco."""
    file_p = tmp_path / "sample_test_page.html"
    file_p.write_text(sample_html_content, encoding="utf-8")
    return file_p


@pytest.fixture
def identical_images_pair(tmp_path: Path) -> tuple[Path, Path]:
    """Cria duas imagens perfeitamente idênticas no disco."""
    base_img = Image.new("RGB", (80, 80), (240, 240, 240))
    curr_img = Image.new("RGB", (80, 80), (240, 240, 240))

    base_p = tmp_path / "baseline_identical.png"
    curr_p = tmp_path / "current_identical.png"

    base_img.save(base_p, format="PNG")
    curr_img.save(curr_p, format="PNG")
    return base_p, curr_p


@pytest.fixture
def divergent_images_pair(tmp_path: Path) -> tuple[Path, Path]:
    """Cria duas imagens com divergência visual controlada acima da tolerância."""
    base_img = Image.new("RGB", (100, 100), (255, 255, 255))
    curr_img = Image.new("RGB", (100, 100), (255, 255, 255))

    # Região 20x20 alterada para preto puro (delta = 255 > 15)
    for y in range(40, 60):
        for x in range(40, 60):
            curr_img.putpixel((x, y), (0, 0, 0))

    base_p = tmp_path / "baseline_divergent.png"
    curr_p = tmp_path / "current_divergent.png"

    base_img.save(base_p, format="PNG")
    curr_img.save(curr_p, format="PNG")
    return base_p, curr_p


@pytest.fixture
def subtle_noise_images_pair(tmp_path: Path) -> tuple[Path, Path]:
    """Cria imagens com variação menor ou igual ao limiar de antialiasing (delta <= 15)."""
    base_img = Image.new("RGB", (50, 50), (200, 200, 200))
    # Delta de 10 por canal (dentro da tolerância de 15)
    curr_img = Image.new("RGB", (50, 50), (190, 190, 190))

    base_p = tmp_path / "baseline_subtle.png"
    curr_p = tmp_path / "current_subtle.png"

    base_img.save(base_p, format="PNG")
    curr_img.save(curr_p, format="PNG")
    return base_p, curr_p


# =============================================================================
# 1. Testes de Unidade e Integração: WebVisualAuditorSuite
# =============================================================================


class TestWebVisualAuditorSuite:
    """Testes unitários e comportamentais da classe WebVisualAuditorSuite."""

    def test_suite_initialization_defaults(self) -> None:
        """Valida inicialização padrão com todos os subsistemas integrados."""
        suite = WebVisualAuditorSuite(offline_mode=True)
        assert isinstance(suite.researcher, WebResearcher)
        assert isinstance(suite.dom_auditor, DOMAuditor)
        assert isinstance(suite.visual_engine, VisualRegressionAuditor)
        assert suite.offline_mode is True

    def test_suite_initialization_with_custom_instances(self) -> None:
        """Valida injeção explícita de instâncias customizadas nos subsistemas."""
        mock_researcher = MagicMock(spec=WebResearcher)
        mock_dom = MagicMock(spec=DOMAuditor)
        mock_vis = MagicMock(spec=VisualRegressionAuditor)

        suite = WebVisualAuditorSuite(
            researcher=mock_researcher,
            dom_auditor=mock_dom,
            visual_engine=mock_vis,
        )

        assert suite.researcher is mock_researcher
        assert suite.dom_auditor is mock_dom
        assert suite.visual_engine is mock_vis

    def test_run_semantic_research_offline(self) -> None:
        """Valida que run_semantic_research retorna lista de referências higienizadas."""
        suite = WebVisualAuditorSuite(offline_mode=True)
        results = suite.run_semantic_research("design tokens", limit=3)

        assert len(results) == 3
        for ref in results:
            assert isinstance(ref, SourceReference)
            assert "design tokens" in ref.title or "design tokens" in ref.snippet
            assert ref.url.startswith("https://") or ref.url.startswith("file://")

    def test_clean_article_html_purges_noise(self, sample_html_content: str) -> None:
        """Valida que clean_article_html purga scripts, styles, svgs e preserva texto nobre."""
        suite = WebVisualAuditorSuite()
        ref = suite.clean_article_html(sample_html_content, url="local://test")

        assert isinstance(ref, SourceReference)
        assert "console.log" not in ref.cleaned_text
        assert "circle cx" not in ref.cleaned_text
        assert "font-family" not in ref.cleaned_text
        assert "Título Principal do Header" in ref.cleaned_text
        assert "Este é o conteúdo do primeiro parágrafo de teste informativo." in ref.cleaned_text

    def test_run_dom_audit_with_raw_html(self, sample_html_content: str) -> None:
        """Valida run_dom_audit ao receber string com código HTML direto."""
        suite = WebVisualAuditorSuite()
        nodes = suite.run_dom_audit(sample_html_content, selectors=["header", "h1", "button"])

        assert len(nodes) >= 3
        tag_names = {node.tag_name for node in nodes}
        assert "header" in tag_names
        assert "h1" in tag_names
        assert "button" in tag_names

        for node in nodes:
            assert isinstance(node, DOMNodeSummary)
            assert node.geometry.width >= 0
            assert node.geometry.height >= 0

    def test_run_dom_audit_with_file_path(self, sample_html_file: Path) -> None:
        """Valida run_dom_audit passando caminho de arquivo local no disco."""
        suite = WebVisualAuditorSuite()
        nodes = suite.run_dom_audit(str(sample_html_file))

        assert len(nodes) > 0
        header_node = next((n for n in nodes if n.tag_name == "header"), None)
        assert header_node is not None
        assert header_node.element_id == "site-header"

    def test_run_visual_audit_identical_images(
        self, identical_images_pair: tuple[Path, Path]
    ) -> None:
        """Valida run_visual_audit entre imagens idênticas (0% diff)."""
        base_p, curr_p = identical_images_pair
        suite = WebVisualAuditorSuite()

        diff_res = suite.run_visual_audit(base_p, curr_p, tolerance=15)
        assert isinstance(diff_res, VisualDiffResult)
        assert diff_res.diff_pixels == 0
        assert diff_res.diff_percentage == 0.0
        assert diff_res.has_divergence is False

    def test_run_visual_audit_divergent_images(
        self, divergent_images_pair: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """Valida run_visual_audit detectando divergência e salvando máscara diferencial."""
        base_p, curr_p = divergent_images_pair
        diff_out = tmp_path / "diff_square.png"
        suite = WebVisualAuditorSuite()

        diff_res = suite.run_visual_audit(base_p, curr_p, diff_out=diff_out, tolerance=15)
        assert diff_res.has_divergence is True
        assert diff_res.diff_pixels == 400
        assert pytest.approx(diff_res.diff_percentage, rel=1e-5) == 4.0
        assert diff_out.exists(), "A máscara diferencial deve ser gerada em disco."

    def test_run_component_audit_with_snapshots(
        self, sample_html_file: Path, tmp_path: Path
    ) -> None:
        """Valida run_component_audit auditando micro-componentes por seletores CSS."""
        suite = WebVisualAuditorSuite()
        diff_dir = tmp_path / "comp_diffs"

        reports = suite.run_component_audit(
            baseline=str(sample_html_file),
            current=str(sample_html_file),
            selectors=["header#site-header", "button#primary-action-btn"],
            diff_dir=diff_dir,
        )

        assert len(reports) == 2
        for r in reports:
            assert isinstance(r, ComponentDiffReport)
            assert r.selector in ["header#site-header", "button#primary-action-btn"]

    def test_run_full_suite_pass_on_identical_targets(
        self, identical_images_pair: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """Valida run_full_suite produzindo status PASS quando não há divergência."""
        base_p, curr_p = identical_images_pair
        out_dir = tmp_path / "suite_pass_out"

        suite = WebVisualAuditorSuite(offline_mode=True)
        config = SuiteConfig(
            baseline_url=str(base_p),
            current_url=str(curr_p),
            search_query="tokens",
            tolerance=15,
            output_dir=str(out_dir),
            capture_fullpage=True,
            save_report_json=True,
        )

        report = suite.run_full_suite(config)

        assert isinstance(report, SuiteAuditReport)
        assert report.overall_status == "PASS"
        assert report.summary_metrics["has_divergence"] is False
        assert report.visual_diff is not None
        assert report.visual_diff.diff_pixels == 0
        assert len(report.research_references) > 0

        report_file = out_dir / "suite_report.json"
        assert report_file.exists()
        saved_data = json.loads(report_file.read_text(encoding="utf-8"))
        assert saved_data["overall_status"] == "PASS"

    def test_run_full_suite_fail_on_divergence(
        self, divergent_images_pair: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """Valida run_full_suite produzindo status FAIL quando há divergência visual."""
        base_p, curr_p = divergent_images_pair
        out_dir = tmp_path / "suite_fail_out"

        suite = WebVisualAuditorSuite()
        config = SuiteConfig(
            baseline_url=str(base_p),
            current_url=str(curr_p),
            output_dir=str(out_dir),
            tolerance=15,
        )

        report = suite.run_full_suite(config)

        assert report.overall_status == "FAIL"
        assert report.summary_metrics["has_divergence"] is True
        assert report.visual_diff is not None
        assert report.visual_diff.diff_pixels == 400

    def test_run_full_suite_with_dict_config(
        self, identical_images_pair: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """Valida que run_full_suite aceita dicionário nativo como configuração."""
        base_p, curr_p = identical_images_pair
        suite = WebVisualAuditorSuite(offline_mode=True)

        config_dict: dict[str, Any] = {
            "baseline_url": str(base_p),
            "current_url": str(curr_p),
            "output_dir": str(tmp_path / "dict_out"),
            "tolerance": 15,
        }

        report = suite.run_full_suite(config_dict)
        assert isinstance(report, SuiteAuditReport)
        assert report.overall_status == "PASS"


# =============================================================================
# 2. Testes de Linha de Comando (CLI): main() e Subcomandos
# =============================================================================


class TestCLIExecution:
    """Testes exaustivos da interface de linha de comando oficial (cli.py)."""

    def test_cli_no_arguments_prints_help_and_returns_zero(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida chamada sem argumentos exibindo mensagem de ajuda com código 0."""
        code = main([])
        assert code == 0
        captured = capsys.readouterr()
        assert "Subcomandos disponíveis" in captured.out or "usage:" in captured.out

    def test_cli_help_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Valida flag --help retornando código 0."""
        code = main(["--help"])
        assert code == 0
        captured = capsys.readouterr()
        assert "web-visual-auditor" in captured.out
        assert "search" in captured.out
        assert "dom-inspect" in captured.out
        assert "visual-diff" in captured.out
        assert "component-diff" in captured.out
        assert "suite" in captured.out

    def test_cli_unknown_subcommand_returns_code_two(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida subcomando inexistente resultando em código de saída 2."""
        code = main(["comando-inexistente"])
        assert code == 2

    # --- Subcomando: search ---

    def test_cli_search_text_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Valida subcomando search em modo texto amigável."""
        code = main(["search", "design system", "--limit", "2", "--offline"])
        assert code == 0
        captured = capsys.readouterr()
        assert "Pesquisa Semântica:" in captured.out
        assert "design system" in captured.out

    def test_cli_search_json_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Valida subcomando search com flag --json emitindo payload válido."""
        code = main(["search", "-q", "css grid", "--limit", "2", "--offline", "--json"])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) == 2
        assert "title" in data[0]
        assert "url" in data[0]

    def test_cli_search_output_file(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida salvamento do resultado da busca em arquivo."""
        out_file = tmp_path / "search_results.txt"
        code = main(
            ["search", "web accessibility", "--limit", "1", "--offline", "-o", str(out_file)]
        )
        assert code == 0
        assert out_file.exists()
        assert "web accessibility" in out_file.read_text(encoding="utf-8")

    def test_cli_search_missing_query_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida erro quando query não é fornecida para o comando search."""
        code = main(["search"])
        assert code == 1
        captured = capsys.readouterr()
        assert "Erro: É necessário informar uma query" in captured.err

    # --- Subcomando: dom-inspect ---

    def test_cli_dom_inspect_html_string(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida inspeção do DOM via string HTML em modo texto."""
        raw_html = "<header><h1>Título H1</h1></header><button id='btn'>Clique</button>"
        code = main(["dom-inspect", "--html", raw_html, "-s", "header,h1,button"])
        assert code == 0
        captured = capsys.readouterr()
        assert "Inspeção de Geometria do DOM" in captured.out
        assert "<header>" in captured.out
        assert "<h1>" in captured.out
        assert "<button>" in captured.out

    def test_cli_dom_inspect_file_json_output(
        self, sample_html_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida dom-inspect em arquivo local emitindo JSON estruturado."""
        code = main(
            [
                "dom-inspect",
                str(sample_html_file),
                "-s",
                "header,button",
                "--json",
            ]
        )
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) >= 2
        assert any(item["tag_name"] == "header" for item in data)
        assert any(item["tag_name"] == "button" for item in data)

    def test_cli_dom_inspect_missing_target_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida erro ao não fornecer alvo para dom-inspect."""
        code = main(["dom-inspect"])
        assert code == 1
        captured = capsys.readouterr()
        assert "Erro: É necessário fornecer uma URL" in captured.err

    # --- Subcomando: visual-diff ---

    def test_cli_visual_diff_identical_returns_code_zero(
        self,
        identical_images_pair: tuple[Path, Path],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida visual-diff com imagens idênticas retornando código 0 (sem divergência)."""
        base_p, curr_p = identical_images_pair
        code = main(["visual-diff", "-b", str(base_p), "-c", str(curr_p), "-t", "15"])
        assert code == 0
        captured = capsys.readouterr()
        assert "SEM DIVERGÊNCIA" in captured.out
        assert "0.0000%" in captured.out

    def test_cli_visual_diff_identical_json(
        self,
        identical_images_pair: tuple[Path, Path],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida visual-diff com imagens idênticas e flag --json."""
        base_p, curr_p = identical_images_pair
        code = main(["visual-diff", "-b", str(base_p), "-c", str(curr_p), "--json"])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["has_divergence"] is False
        assert data["diff_pixels"] == 0

    def test_cli_visual_diff_divergent_returns_code_one(
        self,
        divergent_images_pair: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida visual-diff com divergência retornando código 1 e gerando máscara."""
        base_p, curr_p = divergent_images_pair
        diff_file = tmp_path / "cli_diff_result.png"

        code = main(
            [
                "visual-diff",
                "-b",
                str(base_p),
                "-c",
                str(curr_p),
                "-d",
                str(diff_file),
                "-t",
                "15",
            ]
        )
        assert code == 1  # Código 1 para regressão visual detectada
        captured = capsys.readouterr()
        assert "DIVERGÊNCIA DETECTADA" in captured.out
        assert "400" in captured.out
        assert diff_file.exists(), "Máscara diferencial deve existir."

    def test_cli_visual_diff_divergent_json(
        self,
        divergent_images_pair: tuple[Path, Path],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida visual-diff com divergência e flag --json retornando código 1."""
        base_p, curr_p = divergent_images_pair
        code = main(["visual-diff", "-b", str(base_p), "-c", str(curr_p), "--json"])
        assert code == 1
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["has_divergence"] is True
        assert data["diff_pixels"] == 400

    def test_cli_visual_diff_tolerance_override(
        self,
        subtle_noise_images_pair: tuple[Path, Path],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida que variação dentro da tolerância não gera divergência."""
        base_p, curr_p = subtle_noise_images_pair
        # Tolerância de 15 absorve o delta de 10
        code = main(["visual-diff", "-b", str(base_p), "-c", str(curr_p), "-t", "15"])
        assert code == 0
        captured = capsys.readouterr()
        assert "SEM DIVERGÊNCIA" in captured.out

    def test_cli_visual_diff_missing_file_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida tratamento de erro elegante quando arquivo de imagem não existe."""
        code = main(["visual-diff", "-b", "nao_existe_1.png", "-c", "nao_existe_2.png"])
        assert code == 1
        captured = capsys.readouterr()
        assert "Erro de auditoria:" in captured.err or "não encontrado" in captured.err

    # --- Subcomando: component-diff ---

    def test_cli_component_diff_matched(
        self,
        sample_html_file: Path,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida component-diff para seletores idênticos retornando código 0."""
        diff_dir = tmp_path / "cli_comp_dir"
        code = main(
            [
                "component-diff",
                "-b",
                str(sample_html_file),
                "-c",
                str(sample_html_file),
                "-s",
                "header#site-header",
                "--diff-dir",
                str(diff_dir),
            ]
        )
        assert code == 0
        captured = capsys.readouterr()
        assert "Auditoria de Micro-Componentes" in captured.out
        assert "header#site-header" in captured.out

    def test_cli_component_diff_json(
        self,
        sample_html_file: Path,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida component-diff com flag --json emitindo array JSON válido."""
        code = main(
            [
                "component-diff",
                "-b",
                str(sample_html_file),
                "-c",
                str(sample_html_file),
                "-s",
                "header#site-header,button#primary-action-btn",
                "--json",
            ]
        )
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["selector"] == "header#site-header"

    def test_cli_component_diff_missing_selectors_error(
        self, sample_html_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valida que omissão de --selectors no component-diff dispara erro."""
        # Seletor ausente na linha de comando
        code = main(["component-diff", "-b", str(sample_html_file), "-c", str(sample_html_file)])
        # Argparse rejeita argumentos obrigatórios faltantes com código 2
        assert code == 2

    # --- Subcomando: suite ---

    def test_cli_suite_pass_returns_code_zero(
        self,
        identical_images_pair: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida subcomando suite em cenário sem divergência retornando código 0."""
        base_p, curr_p = identical_images_pair
        out_dir = tmp_path / "cli_suite_out"

        code = main(
            [
                "suite",
                "-b",
                str(base_p),
                "-c",
                str(curr_p),
                "--output-dir",
                str(out_dir),
                "-t",
                "15",
            ]
        )
        assert code == 0
        captured = capsys.readouterr()
        assert "Status Global:     [PASS]" in captured.out

    def test_cli_suite_fail_returns_code_one(
        self,
        divergent_images_pair: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida subcomando suite com regressão retornando código 1."""
        base_p, curr_p = divergent_images_pair
        out_dir = tmp_path / "cli_suite_fail_out"

        code = main(
            [
                "suite",
                "-b",
                str(base_p),
                "-c",
                str(curr_p),
                "--output-dir",
                str(out_dir),
                "-t",
                "15",
            ]
        )
        assert code == 1
        captured = capsys.readouterr()
        assert "Status Global:     [FAIL]" in captured.out

    def test_cli_suite_json_output(
        self,
        identical_images_pair: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Valida subcomando suite com flag --json emitindo relatório estruturado."""
        base_p, curr_p = identical_images_pair
        code = main(
            [
                "suite",
                "-b",
                str(base_p),
                "-c",
                str(curr_p),
                "--output-dir",
                str(tmp_path / "json_suite"),
                "--json",
            ]
        )
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["overall_status"] == "PASS"
        assert "summary_metrics" in data
        assert "baseline_url" in data

    def test_build_parser_structure(self) -> None:
        """Valida a estrutura do parser e o registro dos 5 subcomandos canônicos."""
        import argparse

        parser = build_parser()
        assert parser.prog == "web-visual-auditor"
        subparser_action = next(
            (
                action
                for action in parser._actions
                if isinstance(action, argparse._SubParsersAction)
            ),
            None,
        )
        assert subparser_action is not None
        registered_subcmds = set(subparser_action.choices.keys())
        expected_subcmds = {"search", "dom-inspect", "visual-diff", "component-diff", "suite"}
        assert expected_subcmds.issubset(registered_subcmds)
