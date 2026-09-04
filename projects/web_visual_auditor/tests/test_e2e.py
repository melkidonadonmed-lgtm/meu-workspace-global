"""Suíte de Testes End-to-End (E2E) estruturada em 4 Tiers.

Esta suíte valida a integridade funcional, limites de fronteira (BVA), integração cruzada
entre subsistemas e cenários do mundo real para o pacote web_visual_auditor, utilizando
exclusivamente as classes e métodos reais de produção do pacote:
- SemanticHTMLCleaner e WebResearcher (researcher.py)
- DOMAuditor (dom_auditor.py)
- VisualRegressionAuditor (visual_regression.py)
- ComponentAuditor e sanitize_selector (component_auditor.py)
- WebVisualAuditorSuite (suite.py)
- main (cli.py)
- Exceções e modelos canônicos (exceptions.py, models.py)

Tiers:
- Tier 1: Feature Coverage (Sanity & Happy Path)
- Tier 2: Boundary & Corner Cases (BVA, Limiares, Exceções Genuínas)
- Tier 3: Cross-Feature Integration (DOM -> Isolamento -> Diff -> Máscara em Disco)
- Tier 4: Real-World Scenarios (Artigo Ruidoso & Regressão de Componente de Design System)
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image, ImageDraw

# ==============================================================================
# IMPORTAÇÕES OFICIAIS DO PACOTE WEB_VISUAL_AUDITOR (REQUISITO MANDATÓRIO)
# ==============================================================================
from web_visual_auditor.cli import build_parser
from web_visual_auditor.cli import main as cli_main
from web_visual_auditor.component_auditor import ComponentAuditor, sanitize_selector
from web_visual_auditor.dom_auditor import DOMAuditor
from web_visual_auditor.exceptions import ImageDimensionMismatchError
from web_visual_auditor.models import (
    ComponentDiffReport,
    ComponentSnapshot,
    ComputedElementGeometry,
    DOMNodeSummary,
    SourceReference,
    VisualDiffResult,
)
from web_visual_auditor.researcher import (
    SemanticCleanResult,
    SemanticHTMLCleaner,
    WebResearcher,
)
from web_visual_auditor.suite import WebVisualAuditorSuite
from web_visual_auditor.visual_regression import VisualRegressionAuditor

# Fixtures locais estáticas e geradores sintéticos
from .fixtures import SAMPLE_NOISY_ARTICLE_HTML, SAMPLE_PAGE_HTML
from .fixtures.image_fixtures import (
    generate_dimension_mismatch_pair,
    generate_divergent_square_pair,
    generate_identical_pair,
    generate_subtle_noise_pair,
    save_image_pair_to_disk,
)

# Diretório base para persistência auditável de artefatos de teste
_PACKAGE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# TIER 1: FEATURE COVERAGE (HAPPY PATHS & CORE CONTRACTS)
# ==============================================================================


class TestTier1FeatureCoverage:
    """Validação da cobertura primária de cada funcionalidade com classes reais do pacote."""

    def test_r1_semantic_cleaning_basic_happy_path(self) -> None:
        """R1: Valida a remoção cirúrgica de ruído usando SemanticHTMLCleaner real."""
        raw_html = (
            "<div>"
            "<script>alert('malicious');</script>"
            "<style>body { color: red; }</style>"
            "<h1>Título do Artigo</h1>"
            "<svg><path d='M10 10'/></svg>"
            "<p>Parágrafo de texto informativo e limpo.</p>"
            "<noscript>Aviso desnecessário</noscript>"
            "<a href='https://artigo.local/ref1'>Referência 1</a>"
            "</div>"
        )
        cleaner = SemanticHTMLCleaner()

        # 1. Limpeza via instância
        clean_result = cleaner.clean_html(raw_html)
        assert isinstance(clean_result, SemanticCleanResult)
        cleaned_text = clean_result.cleaned_text

        # Asserções de expurgo de ruído
        assert "alert" not in cleaned_text
        assert "color: red" not in cleaned_text
        assert "Aviso desnecessário" not in cleaned_text
        assert "Título do Artigo" in cleaned_text
        assert "Parágrafo de texto informativo e limpo." in cleaned_text

        # 2. Desempacotamento transparente (text, refs)
        text_unpacked, refs_unpacked = cleaner.clean_and_extract(raw_html)
        assert text_unpacked == cleaned_text
        assert len(refs_unpacked) == 1
        assert refs_unpacked[0].url == "https://artigo.local/ref1"

        # 3. Invocação estática e de classe de SemanticHTMLCleaner
        static_cleaned = SemanticHTMLCleaner.clean(raw_html)
        assert "alert" not in static_cleaned
        assert "Título do Artigo" in static_cleaned

        class_cleaned = SemanticHTMLCleaner.clean_html(raw_html)
        assert "alert" not in class_cleaned.cleaned_text
        assert "Título do Artigo" in class_cleaned.cleaned_text

    def test_r2_dom_key_elements_presence_in_fixture(self) -> None:
        """R2: Valida extração de elementos e geometrias usando DOMAuditor().inspect_html()."""
        assert SAMPLE_PAGE_HTML.exists(), "A fixture sample_page.html deve existir em disco."
        html_content = SAMPLE_PAGE_HTML.read_text(encoding="utf-8")

        auditor = DOMAuditor(force_fallback=True)
        nodes: list[DOMNodeSummary] = auditor.inspect_html(html_content)

        assert len(nodes) >= 6, "Deve extrair ao menos header, nav, h1, main, article, buttons."

        # Validação do header
        header_node = auditor.find_required_node(nodes, "#main-header")
        assert header_node.tag_name == "header"
        assert "site-header" in header_node.classes
        assert header_node.is_visible is True
        assert header_node.geometry.width > 0
        assert header_node.geometry.height > 0

        # Validação do nav
        nav_node = auditor.find_required_node(nodes, "#navbar")
        assert nav_node.tag_name == "nav"
        assert "main-nav" in nav_node.classes
        assert nav_node.is_visible is True

        # Validação do h1
        h1_node = auditor.find_required_node(nodes, "#page-title")
        assert h1_node.tag_name == "h1"
        assert "heading-primary" in h1_node.classes
        assert h1_node.is_visible is True

        # Validação do main e article
        main_node = auditor.find_required_node(nodes, "#main-content")
        assert main_node.tag_name == "main"

        article_node = auditor.find_required_node(nodes, "#featured-article")
        assert article_node.tag_name == "article"

        # Validação dos botões
        btn_primary = auditor.find_required_node(nodes, "#primary-action-btn")
        assert btn_primary.tag_name == "button"
        assert btn_primary.is_visible is True

        btn_secondary = auditor.find_required_node(nodes, "#secondary-btn")
        assert btn_secondary.tag_name == "button"
        assert btn_secondary.is_visible is True

    def test_r3_visual_diff_identical_images_zero_divergence(self) -> None:
        """R3: Valida 0% de divergência via VisualRegressionAuditor().compare_images()."""
        baseline, current = generate_identical_pair(width=100, height=100, color=(255, 255, 255))
        auditor = VisualRegressionAuditor(channel_tolerance=15)

        diff_result: VisualDiffResult = auditor.compare_images(baseline, current)

        assert isinstance(diff_result, VisualDiffResult)
        assert diff_result.total_pixels == 10000
        assert diff_result.diff_pixels == 0
        assert diff_result.diff_percentage == 0.0
        assert diff_result.has_divergence is False

    def test_r4_component_snapshot_metadata_contract(self, tmp_path: Path) -> None:
        """R4: Valida recorte e contrato de metadados via ComponentAuditor().capture_component_from_image()."""
        # Cria tela sintética 400x300 e desenha um botão de 160x42 em (32, 200)
        fullpage = Image.new("RGB", (400, 300), color=(240, 240, 240))
        draw = ImageDraw.Draw(fullpage)
        draw.rectangle([32, 200, 32 + 160 - 1, 200 + 42 - 1], fill=(37, 99, 235))

        fullpage_path = tmp_path / "page_capture.png"
        fullpage.save(fullpage_path)

        comp_output = tmp_path / "diff_primary-action-btn.png"
        auditor = ComponentAuditor()

        snapshot: ComponentSnapshot = auditor.capture_component_from_image(
            fullpage_image=fullpage_path,
            selector="button#primary-action-btn",
            bounding_box=(32, 200, 160, 42),
            output_path=comp_output,
        )

        assert isinstance(snapshot, ComponentSnapshot)
        assert snapshot.selector == "button#primary-action-btn"
        assert snapshot.dimensions == (160, 42)
        assert snapshot.geometry is not None
        assert snapshot.geometry.x == 32.0
        assert snapshot.geometry.y == 200.0
        assert snapshot.geometry.width == 160.0
        assert snapshot.geometry.height == 42.0
        assert snapshot.is_visible is True
        assert Path(snapshot.screenshot_path).exists()

        # Validação do pixel recortado
        with Image.open(snapshot.screenshot_path) as cropped_img:
            assert cropped_img.size == (160, 42)
            assert cropped_img.getpixel((10, 10)) == (37, 99, 235)

    def test_r5_cli_subcommands_specification(self) -> None:
        """R5: Valida a CLI executando subcomando real search via cli_main(["search", ...])."""
        # Validação da árvore de subparsers
        parser = build_parser()
        subparser_action = next(
            action for action in parser._actions if action.dest == "subcommand"
        )
        subcommand_choices = set(subparser_action.choices.keys())
        expected_subcommands = {"search", "dom-inspect", "visual-diff", "component-diff", "suite"}
        assert expected_subcommands.issubset(subcommand_choices)

        # Execução real do subcomando search em modo offline
        exit_code = cli_main(["search", "design system visual regression", "--offline", "-l", "3"])
        assert exit_code == 0, "A CLI search em modo offline deve retornar código POSIX 0."


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES (BVA & EXCEPTION HANDLING)
# ==============================================================================


class TestTier2BoundaryAndCornerCases:
    """Validação rigorosa de fronteiras numéricas (BVA), tolerância de canal e exceções."""

    def test_bva_antialiasing_channel_tolerance_within_15(self) -> None:
        """BVA: Variação de canal com delta <= 15 NÃO deve divergir via VisualRegressionAuditor."""
        # Baseline: branco puro (255, 255, 255)
        # Current: cinza muito claro (240, 240, 240) -> delta = 15 exatamente
        baseline, current = generate_subtle_noise_pair(
            width=100, height=100, base_color=(255, 255, 255), noise_delta=15
        )
        auditor = VisualRegressionAuditor(channel_tolerance=15)
        res = auditor.compare_images(baseline, current, tolerance=15)

        assert res.total_pixels == 10000
        assert res.diff_pixels == 0
        assert res.diff_percentage == 0.0
        assert res.has_divergence is False

    def test_bva_antialiasing_channel_divergence_above_15(self) -> None:
        """BVA: Variação de canal com delta == 16 (> 15) DEVE divergir via VisualRegressionAuditor."""
        # Baseline: branco (255, 255, 255)
        # Current: cinza (239, 239, 239) -> delta = |255 - 239| = 16 > 15
        baseline = Image.new("RGB", (100, 100), (255, 255, 255))
        current = Image.new("RGB", (100, 100), (239, 239, 239))

        auditor = VisualRegressionAuditor(channel_tolerance=15)
        res = auditor.compare_images(baseline, current, tolerance=15)

        assert res.total_pixels == 10000
        assert res.diff_pixels == 10000
        assert res.diff_percentage == 100.0
        assert res.has_divergence is True

    def test_bva_mathematical_square_divergence_exact_4_percent(self) -> None:
        """BVA: Quadrado 20x20 em canvas 100x100 produz exatamente 400 pixels e 4.0% de diff."""
        baseline, current = generate_divergent_square_pair(
            width=100,
            height=100,
            base_color=(255, 255, 255),
            square_color=(0, 0, 0),
            square_size=20,
            top_left=(40, 40),
        )
        auditor = VisualRegressionAuditor(channel_tolerance=15)
        res = auditor.compare_images(baseline, current)

        assert res.total_pixels == 10000
        assert res.diff_pixels == 400
        assert pytest.approx(res.diff_percentage, rel=1e-5) == 4.0
        assert res.has_divergence is True

    def test_bva_dimension_mismatch_raises_appropriate_exception(self) -> None:
        """BVA: Disparo genuíno de ImageDimensionMismatchError pelo motor do pacote."""
        img_a, img_b = generate_dimension_mismatch_pair(dim_a=(100, 100), dim_b=(120, 100))
        auditor = VisualRegressionAuditor()

        # Disparo genuíno vindo de compare_images (sem raise manual dentro do teste!)
        with pytest.raises(ImageDimensionMismatchError) as exc_info:
            auditor.compare_images(img_a, img_b)

        assert exc_info.value.baseline_dims == (100, 100)
        assert exc_info.value.current_dims == (120, 100)
        assert "Dimensões incompatíveis" in str(exc_info.value)

    def test_bva_hidden_element_is_marked_not_visible(self) -> None:
        """BVA: Elementos com display:none e atributo nativo 'hidden' marcados is_visible=False."""
        html_content = SAMPLE_PAGE_HTML.read_text(encoding="utf-8")
        auditor = DOMAuditor(force_fallback=True)
        nodes = auditor.inspect_html(html_content)

        # 1. Elemento com display: none e classe hidden-box da fixture sample_page.html
        hidden_node = auditor.find_required_node(nodes, "#hidden-element")
        assert hidden_node.is_visible is False, "Nó #hidden-element deve ser marcado is_visible=False"

        # 2. Elemento com atributo nativo HTML5 'hidden'
        native_hidden_html = "<div><button id='btn-native-hidden' hidden>Oculto</button></div>"
        native_nodes = auditor.inspect_html(native_hidden_html)
        native_btn = auditor.find_required_node(native_nodes, "#btn-native-hidden")
        assert native_btn.is_visible is False, "Botão com atributo HTML5 'hidden' deve ser is_visible=False"

        # 3. Elemento com largura 0 (dimensão zero)
        zero_dim_html = "<div><button id='btn-zero-w' style='width: 0px; height: 50px;'>Zero</button></div>"
        zero_nodes = auditor.inspect_html(zero_dim_html)
        zero_btn = auditor.find_required_node(zero_nodes, "#btn-zero-w")
        assert zero_btn.is_visible is False, "Elemento com width=0 deve ser marcado is_visible=False"

    def test_bva_empty_and_whitespace_html_handling(self) -> None:
        """BVA: Tratamento gracioso de strings HTML vazias ou contendo apenas espaços."""
        cleaner = SemanticHTMLCleaner()
        empty_inputs = ["", "   ", "\n\t  \n"]
        for raw in empty_inputs:
            cleaned = cleaner.clean_text(raw)
            assert cleaned == ""

            clean_res = cleaner.clean_html(raw)
            assert clean_res.cleaned_text == ""
            assert clean_res.references == []


# ==============================================================================
# TIER 3: CROSS-FEATURE INTEGRATION TESTS
# ==============================================================================


class TestTier3CrossFeatureIntegration:
    """Integração cruzada entre subsistemas (DOM -> Recorte -> Diff -> Máscara em Disco)."""

    def test_cross_feature_selector_sanitization_for_filesystem(self) -> None:
        """Cross-Feature: Sanitização de seletores via ComponentAuditor.sanitize_selector."""
        selectors_to_test = [
            ("button.btn-primary", "diff_button_btn-primary.png"),
            ("#main-header > nav ul li:first-child", "diff_main-header_nav_ul_li_first-child.png"),
            ("div[data-testid='card.large']", "diff_div_data-testid_card_large.png"),
            (".card__title--active", "diff_card__title--active.png"),
        ]

        for selector, expected_filename in selectors_to_test:
            sanitized = sanitize_selector(selector)
            generated_filename = f"diff_{sanitized}.png"
            assert generated_filename == expected_filename

    def test_cross_feature_visual_diff_mask_generation_and_disk_save(
        self, tmp_path: Path
    ) -> None:
        """Cross-Feature: Gravação física de diff_result.png e diff_<selector>.png com pixel #FF0000."""
        # 1. Geração de baseline e current divergentes
        baseline, current = generate_divergent_square_pair(
            width=100, height=100, square_size=20, top_left=(40, 40)
        )

        # 2. Execução pelo motor VisualRegressionAuditor com gravação real de diff_result.png
        diff_target_file = tmp_path / "diff_result.png"
        auditor = VisualRegressionAuditor(channel_tolerance=15)
        diff_result = auditor.compare_images(
            baseline_img=baseline,
            current_img=current,
            diff_output_path=diff_target_file,
        )

        assert diff_result.diff_pixels == 400
        assert diff_result.has_divergence is True
        assert diff_target_file.exists(), "O arquivo diff_result.png DEVE ser gravado fisicamente em disco."

        # Cópia permanente para tests/, artifacts/ e raiz do pacote
        tests_dir = Path(__file__).resolve().parent
        tests_diff = tests_dir / "diff_result.png"
        tests_diff.write_bytes(diff_target_file.read_bytes())
        assert tests_diff.exists(), "diff_result.png deve persistir em tests/"

        artifacts_dir = _PACKAGE_DIR / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        persisted_diff = artifacts_dir / "diff_result.png"
        persisted_diff.write_bytes(diff_target_file.read_bytes())
        assert persisted_diff.exists()

        root_diff = _PACKAGE_DIR / "diff_result.png"
        root_diff.write_bytes(diff_target_file.read_bytes())
        assert root_diff.exists()

        # Validação física dos pixels na imagem salva em disco (vermelho puro #FF0000)
        with Image.open(diff_target_file) as saved_img:
            assert saved_img.size == (100, 100)
            saved_rgba = saved_img.convert("RGBA")
            pixels = saved_rgba.load()

            red_pixels_count = 0
            for y in range(100):
                for x in range(100):
                    px = pixels[x, y]
                    if px == (255, 0, 0, 255):
                        red_pixels_count += 1
                        assert 40 <= x < 60, f"Pixel vermelho fora da área X esperada: x={x}"
                        assert 40 <= y < 60, f"Pixel vermelho fora da área Y esperada: y={y}"

            assert red_pixels_count == 400, (
                f"Exatamente 400 pixels devem ser vermelho puro #FF0000, encontrado: {red_pixels_count}"
            )

        # 3. Execução pelo motor ComponentAuditor com gravação real de diff_<selector>.png
        base_btn_img = Image.new("RGB", (100, 40), color=(0, 128, 0))
        curr_btn_img = Image.new("RGB", (100, 40), color=(0, 128, 0))
        draw_curr = ImageDraw.Draw(curr_btn_img)
        draw_curr.rectangle([10, 10, 29, 29], fill=(200, 0, 0))  # Regressão 20x20 = 400 px

        base_btn_path = tmp_path / "base_btn.png"
        curr_btn_path = tmp_path / "curr_btn.png"
        diff_comp_target = tmp_path / "diff_button_checkout.png"
        base_btn_img.save(base_btn_path)
        curr_btn_img.save(curr_btn_path)

        snap_base = ComponentSnapshot(
            selector="button.checkout",
            dimensions=(100, 40),
            screenshot_path=str(base_btn_path),
        )
        snap_curr = ComponentSnapshot(
            selector="button.checkout",
            dimensions=(100, 40),
            screenshot_path=str(curr_btn_path),
        )

        comp_auditor = ComponentAuditor()
        comp_report: ComponentDiffReport = comp_auditor.compare_component_snapshots(
            baseline_snapshot=snap_base,
            current_snapshot=snap_curr,
            diff_output_path=diff_comp_target,
        )

        assert comp_report.status == "diverged"
        assert comp_report.diff_result is not None
        assert comp_report.diff_result.diff_pixels == 400
        assert diff_comp_target.exists(), "O arquivo diff_<selector>.png DEVE ser gravado fisicamente em disco."

        # Cópia permanente para tests/, artifacts/ e raiz
        tests_comp_diff = tests_dir / "diff_button_checkout.png"
        tests_comp_diff.write_bytes(diff_comp_target.read_bytes())
        assert tests_comp_diff.exists(), "diff_button_checkout.png deve persistir em tests/"

        persisted_comp_diff = artifacts_dir / "diff_button_checkout.png"
        persisted_comp_diff.write_bytes(diff_comp_target.read_bytes())
        assert persisted_comp_diff.exists()

        root_comp_diff = _PACKAGE_DIR / "diff_button_checkout.png"
        root_comp_diff.write_bytes(diff_comp_target.read_bytes())
        assert root_comp_diff.exists()

        with Image.open(diff_comp_target) as comp_img:
            comp_rgba = comp_img.convert("RGBA")
            assert comp_rgba.getpixel((15, 15)) == (255, 0, 0, 255)

    def test_cross_feature_dom_extraction_matches_html_semantics(self) -> None:
        """Cross-Feature: Extração do modelo de nós e geometrias via DOMAuditor."""
        html_content = SAMPLE_PAGE_HTML.read_text(encoding="utf-8")
        auditor = DOMAuditor(force_fallback=True)
        nodes = auditor.inspect_html(html_content)

        extracted_tags = {n.tag_name for n in nodes}
        required_tags = {"header", "nav", "h1", "main", "article", "button"}
        assert required_tags.issubset(extracted_tags)

        # Validação de integridade semântica e encadeamento geométrico
        for node in nodes:
            assert isinstance(node, DOMNodeSummary)
            assert isinstance(node.geometry, ComputedElementGeometry)
            assert node.geometry.width >= 0
            assert node.geometry.height >= 0
            assert node.geometry.x >= 0
            assert node.geometry.y >= 0


# ==============================================================================
# TIER 4: REAL-WORLD SCENARIOS (END-TO-END WORKLOADS)
# ==============================================================================


class TestTier4RealWorldScenarios:
    """Validação de casos de uso completos com alta densidade de ruído e cenários de UI."""

    def test_real_world_noisy_article_full_semantic_scrubbing(self) -> None:
        """Tier 4: Higienização semântica via WebResearcher().extract_from_html()."""
        assert SAMPLE_NOISY_ARTICLE_HTML.exists()
        raw_html = SAMPLE_NOISY_ARTICLE_HTML.read_text(encoding="utf-8")

        researcher = WebResearcher()
        ref: SourceReference = researcher.extract_from_html(
            raw_html=raw_html,
            url="local://sample_noisy_article",
        )

        assert isinstance(ref, SourceReference)
        cleaned_text = ref.cleaned_text

        # Asserts de Ausência de Ruído (Zero Contaminação)
        assert "dataLayer" not in cleaned_text
        assert "gtag" not in cleaned_text
        assert "UA-99999999-1" not in cleaned_text
        assert "telemetry beacon" not in cleaned_text.lower()
        assert "ad-banner" not in cleaned_text
        assert "SVG TEXT MUST BE PURGED" not in cleaned_text
        assert "Atenção: Este site requer JavaScript" not in cleaned_text
        assert "Analytics tracking snippet" not in cleaned_text
        assert "Alerta exclusivo para navegadores legados" not in cleaned_text

        # Asserts de Preservação Editorial Nobre
        assert "Revolução na Auditoria Visual de Interfaces Web" in cleaned_text
        assert "Fundamentos da Auditoria Diferencial" in cleaned_text
        assert "automação de inspeção de regressão visual" in cleaned_text
        assert "A verdadeira robustez de um sistema de design" in cleaned_text
        assert "Isolamento Semântico e Remoção de Ruído" in cleaned_text
        assert "Eliminação completa de nós de scripts executáveis" in cleaned_text

        # Asserts de Extração de Metadados
        assert ref.title == "Revolução na Auditoria Visual de Interfaces Web"
        assert len(ref.snippet) >= 20

    def test_real_world_design_system_component_regression_simulation(
        self, tmp_path: Path
    ) -> None:
        """Tier 4: Simulação de regressão de componente de Design System via ComponentAuditor."""
        # Botão primário azul: (37, 99, 235) / 160x42
        btn_width, btn_height = 160, 42
        baseline_btn = Image.new("RGB", (btn_width, btn_height), (37, 99, 235))

        # Botão current: sofreu regressão de estilo em uma área interna de 40x20 pixels (800 px)
        current_btn = Image.new("RGB", (btn_width, btn_height), (37, 99, 235))
        draw_curr = ImageDraw.Draw(current_btn)
        draw_curr.rectangle([20, 10, 59, 29], fill=(239, 68, 68))  # Vermelho de regressão

        # Salva em disco simulando artefatos de screenshot
        b_path, c_path = save_image_pair_to_disk(
            baseline_btn,
            current_btn,
            output_dir=tmp_path,
            baseline_filename="baseline_button.png",
            current_filename="current_button.png",
        )
        assert b_path.exists()
        assert c_path.exists()

        diff_output_file = tmp_path / "diff_primary-action-btn.png"

        snap_base = ComponentSnapshot(
            selector="button#primary-action-btn",
            dimensions=(btn_width, btn_height),
            screenshot_path=str(b_path),
            geometry=ComputedElementGeometry(x=32.0, y=200.0, width=160.0, height=42.0),
        )
        snap_curr = ComponentSnapshot(
            selector="button#primary-action-btn",
            dimensions=(btn_width, btn_height),
            screenshot_path=str(c_path),
            geometry=ComputedElementGeometry(x=32.0, y=200.0, width=160.0, height=42.0),
        )

        comp_auditor = ComponentAuditor()
        report: ComponentDiffReport = comp_auditor.compare_component_snapshots(
            baseline_snapshot=snap_base,
            current_snapshot=snap_curr,
            diff_output_path=diff_output_file,
        )

        expected_total = 160 * 42  # 6720 pixels
        expected_diff = 40 * 20  # 800 pixels
        expected_pct = (800 / 6720) * 100.0  # ~11.90476%

        assert report.status == "diverged"
        assert report.geometry_changed is False
        assert report.diff_result is not None
        assert report.diff_result.total_pixels == expected_total
        assert report.diff_result.diff_pixels == expected_diff
        assert pytest.approx(report.diff_result.diff_percentage, rel=1e-4) == expected_pct
        assert report.diff_result.has_divergence is True

        assert diff_output_file.exists()
        with Image.open(diff_output_file) as diff_img:
            diff_rgba = diff_img.convert("RGBA")
            # O pixel na coordenada da regressão deve estar marcado com vermelho puro
            assert diff_rgba.getpixel((30, 15)) == (255, 0, 0, 255)

    def test_full_suite_pipeline_integration(self, tmp_path: Path) -> None:
        """Tier 4: Validação da orquestração unificada via WebVisualAuditorSuite real."""
        baseline_img, current_img = generate_divergent_square_pair(
            width=100, height=100, square_size=10, top_left=(45, 45)
        )
        b_path, c_path = save_image_pair_to_disk(
            baseline_img,
            current_img,
            output_dir=tmp_path,
            baseline_filename="suite_baseline.png",
            current_filename="suite_current.png",
        )

        suite = WebVisualAuditorSuite(offline_mode=True)
        suite_diff = tmp_path / "diff_result.png"

        # 1. Auditoria DOM
        dom_nodes = suite.run_dom_audit(SAMPLE_PAGE_HTML.read_text(encoding="utf-8"))
        assert len(dom_nodes) >= 6

        # 2. Auditoria Visual Fullpage
        visual_res = suite.run_visual_audit(
            baseline=b_path,
            current=c_path,
            diff_out=suite_diff,
        )
        assert visual_res.diff_pixels == 100
        assert visual_res.has_divergence is True
        assert suite_diff.exists()

        # 3. Pesquisa Semântica integrada
        sources = suite.run_semantic_research("design system visual regression", limit=2)
        assert len(sources) >= 1
        assert sources[0].url.startswith("http")
