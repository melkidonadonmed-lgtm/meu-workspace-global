"""Suíte de testes para o módulo dom_auditor (DOM Geometry Inspector).

Cobre:
- Inspeção determinística usando a fixture sample_page.html (via inspect_url e inspect_html)
- Detecção dos elementos obrigatórios: header, main, article, button, nav, h1
- Validação rigorosa dos valores de geometria (x, y, width, height) e visibilidade (is_visible)
- Seletores customizados e busca unívoca de nós (find_node, find_required_node)
- Tratamento de exceções e timeouts (NavigationTimeoutError, ElementNotFoundError)
- Modo headless Playwright e fallback estrutural resiliente offline
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from web_visual_auditor.dom_auditor import DOMAuditor
from web_visual_auditor.exceptions import (
    AuditorError,
    DOMAuditError,
    ElementNotFoundError,
    NavigationTimeoutError,
    PageNavigationTimeoutError,
)
from web_visual_auditor.models import (
    ComputedElementGeometry,
    DOMNodeSummary,
)

# Resolução de caminhos e fixtures de teste
_TESTS_DIR = Path(__file__).resolve().parent
FIXTURE_SAMPLE_PAGE = _TESTS_DIR / "fixtures" / "sample_page.html"


# ==============================================================================
# 1. Testes de Inicialização e Configuração
# ==============================================================================


def test_dom_auditor_initialization_defaults() -> None:
    """Valida valores padrão na inicialização do DOMAuditor."""
    auditor = DOMAuditor()
    assert auditor.headless is True
    assert auditor.default_timeout_ms == 15000
    assert auditor.viewport_size == {"width": 1280, "height": 800}
    assert auditor.force_fallback is False
    assert len(auditor.DEFAULT_KEY_SELECTORS) >= 6
    assert "header" in auditor.DEFAULT_KEY_SELECTORS
    assert "main" in auditor.DEFAULT_KEY_SELECTORS
    assert "article" in auditor.DEFAULT_KEY_SELECTORS
    assert "button" in auditor.DEFAULT_KEY_SELECTORS
    assert "nav" in auditor.DEFAULT_KEY_SELECTORS
    assert "h1" in auditor.DEFAULT_KEY_SELECTORS


def test_dom_auditor_custom_config() -> None:
    """Valida configurações personalizadas de viewport e timeout."""
    custom_viewport = {"width": 1920, "height": 1080}
    auditor = DOMAuditor(
        headless=False,
        default_timeout_ms=5000,
        viewport_size=custom_viewport,
        force_fallback=True,
    )
    assert auditor.headless is False
    assert auditor.default_timeout_ms == 5000
    assert auditor.viewport_size == custom_viewport
    assert auditor.force_fallback is True
    assert auditor.is_browser_available is False


# ==============================================================================
# 2. Testes de Detecção de Elementos Obrigatórios (sample_page.html)
# ==============================================================================


@pytest.mark.parametrize("force_fallback", [False, True])
def test_detect_all_mandatory_elements_in_sample_page(force_fallback: bool) -> None:
    """Valida a detecção determinística dos elementos obrigatórios:

    header, main, article, button, nav, h1 em ambos os modos (headless e fallback).
    """
    assert FIXTURE_SAMPLE_PAGE.exists(), "A fixture sample_page.html deve existir em disco."
    auditor = DOMAuditor(force_fallback=force_fallback)

    nodes = auditor.inspect_url(str(FIXTURE_SAMPLE_PAGE))
    assert len(nodes) >= 6, "Deve extrair ao menos os 6 nós estruturais principais."

    tags_found = {node.tag_name for node in nodes}
    mandatory_tags = {"header", "main", "article", "button", "nav", "h1"}
    assert mandatory_tags.issubset(tags_found), (
        f"Tags obrigatórias ausentes: {mandatory_tags - tags_found}"
    )

    # 1. Header
    header_node = auditor.find_required_node(nodes, "header")
    assert header_node.tag_name == "header"
    assert header_node.element_id == "main-header"
    assert "site-header" in header_node.classes
    assert header_node.is_visible is True

    # 2. Nav
    nav_node = auditor.find_required_node(nodes, "nav")
    assert nav_node.tag_name == "nav"
    assert nav_node.element_id == "navbar"
    assert "main-nav" in nav_node.classes
    assert nav_node.is_visible is True

    # 3. Main
    main_node = auditor.find_required_node(nodes, "main")
    assert main_node.tag_name == "main"
    assert main_node.element_id == "main-content"
    assert "site-main" in main_node.classes
    assert main_node.is_visible is True

    # 4. H1
    h1_node = auditor.find_required_node(nodes, "h1")
    assert h1_node.tag_name == "h1"
    assert h1_node.element_id == "page-title"
    assert "heading-primary" in h1_node.classes
    assert "Auditoria Visual e Geométrica do DOM" in (h1_node.text_content or "")
    assert h1_node.is_visible is True

    # 5. Article
    article_node = auditor.find_required_node(nodes, "article")
    assert article_node.tag_name == "article"
    assert article_node.element_id == "featured-article"
    assert "article-container" in article_node.classes
    assert article_node.is_visible is True

    # 6. Buttons
    buttons = [n for n in nodes if n.tag_name == "button"]
    assert len(buttons) >= 2, "Devem ser encontrados pelo menos 2 botões de ação."

    btn_primary = auditor.find_required_node(nodes, "#primary-action-btn")
    assert btn_primary.tag_name == "button"
    assert "btn-primary" in btn_primary.classes
    assert "Executar Auditoria" in (btn_primary.text_content or "")
    assert btn_primary.is_visible is True

    btn_secondary = auditor.find_required_node(nodes, "#secondary-btn")
    assert btn_secondary.tag_name == "button"
    assert "btn-secondary" in btn_secondary.classes
    assert "Cancelar" in (btn_secondary.text_content or "")
    assert btn_secondary.is_visible is True


# ==============================================================================
# 3. Testes de Geometria Computada e Visibilidade
# ==============================================================================


def test_geometry_values_and_css_bounding_boxes() -> None:
    """Valida que as dimensões CSS de sample_page.html são fielmente extraídas."""
    html_content = FIXTURE_SAMPLE_PAGE.read_text(encoding="utf-8")
    auditor = DOMAuditor(force_fallback=True)
    nodes = auditor.inspect_html(html_content)

    # 1. Header (width: 100% -> 1280px, height: 80px)
    header = auditor.find_required_node(nodes, "header#main-header")
    assert isinstance(header.geometry, ComputedElementGeometry)
    assert header.geometry.height == 80.0
    assert header.geometry.width == 1280.0
    assert header.geometry.area == 1280.0 * 80.0
    assert header.is_visible is True

    # 2. Article (width: 800px)
    article = auditor.find_required_node(nodes, "article#featured-article")
    assert article.geometry.width == 800.0
    assert article.is_visible is True

    # 3. Botão Primário (width: 160px, height: 42px)
    btn_primary = auditor.find_required_node(nodes, "#primary-action-btn")
    assert btn_primary.geometry.width == 160.0
    assert btn_primary.geometry.height == 42.0
    assert btn_primary.geometry.area == 160.0 * 42.0
    assert btn_primary.is_visible is True

    # 4. Botão Secundário (width: 120px, height: 42px)
    btn_secondary = auditor.find_required_node(nodes, "#secondary-btn")
    assert btn_secondary.geometry.width == 120.0
    assert btn_secondary.geometry.height == 42.0
    assert btn_secondary.is_visible is True


def test_hidden_and_zero_dim_elements_visibility() -> None:
    """Valida a classificação estrita de nós ocultos e de dimensão zero."""
    html_content = FIXTURE_SAMPLE_PAGE.read_text(encoding="utf-8")
    auditor = DOMAuditor(force_fallback=True)

    # Inspeciona incluindo seletores para nós invisíveis
    selectors = auditor.DEFAULT_KEY_SELECTORS + ["#hidden-element", "#zero-dim-element"]
    nodes = auditor.inspect_html(html_content, selectors=selectors)

    # Elemento com display: none
    hidden_node = auditor.find_required_node(nodes, "#hidden-element")
    assert hidden_node.is_visible is False
    assert hidden_node.geometry.width == 0.0
    assert hidden_node.geometry.height == 0.0

    # Elemento com dimensões 0x0
    zero_node = auditor.find_required_node(nodes, "#zero-dim-element")
    assert zero_node.is_visible is False
    assert zero_node.geometry.width == 0.0
    assert zero_node.geometry.height == 0.0


# ==============================================================================
# 4. Testes de Seletores Customizados e Métodos Utilitários
# ==============================================================================


def test_custom_selectors_filter() -> None:
    """Verifica que apenas os seletores solicitados são extraídos quando especificados."""
    html_content = (
        "<div>"
        "  <header id='hdr'>Topo</header>"
        "  <nav id='nav'>Links</nav>"
        "  <button id='btn1' class='btn-primary'>Ação 1</button>"
        "  <button id='btn2' class='btn-secondary'>Ação 2</button>"
        "  <footer>Rodapé</footer>"
        "</div>"
    )
    auditor = DOMAuditor(force_fallback=True)

    # Solicita exclusivamente seletores de botão
    nodes = auditor.inspect_html(html_content, selectors=["button.btn-primary"])
    assert len(nodes) == 1
    assert nodes[0].element_id == "btn1"
    assert nodes[0].tag_name == "button"
    assert "btn-primary" in nodes[0].classes


def test_find_node_and_find_required_node() -> None:
    """Testa localização unívoca e lançamento de exceção para seletores inexistentes."""
    geo = ComputedElementGeometry(x=0.0, y=0.0, width=100.0, height=40.0)
    mock_nodes = [
        DOMNodeSummary(
            tag_name="button",
            element_id="submit-action",
            classes=["btn", "btn-success"],
            is_visible=True,
            geometry=geo,
            selector="button#submit-action",
        ),
        DOMNodeSummary(
            tag_name="h1",
            element_id="main-title",
            classes=["heading"],
            is_visible=True,
            geometry=geo,
            selector="h1#main-title",
        ),
    ]
    auditor = DOMAuditor()

    # Sucessos
    assert auditor.find_node(mock_nodes, "button") is not None
    assert auditor.find_node(mock_nodes, "#submit-action") is not None
    assert auditor.find_node(mock_nodes, ".btn-success") is not None
    assert auditor.find_node(mock_nodes, "h1") is not None

    # Falha graciosa em find_node
    assert auditor.find_node(mock_nodes, "article") is None
    assert auditor.find_node(mock_nodes, "#inexistent-id") is None

    # Falha estrita em find_required_node
    with pytest.raises(ElementNotFoundError) as exc_info:
        auditor.find_required_node(mock_nodes, "article")
    assert exc_info.value.selector == "article"
    assert isinstance(exc_info.value, DOMAuditError)
    assert isinstance(exc_info.value, AuditorError)


# ==============================================================================
# 5. Testes de Tratamento de Exceções, Timeout e Resiliência
# ==============================================================================


def test_inspect_url_timeout_raises_when_requested() -> None:
    """Garante que PageNavigationTimeoutError é lançado com raise_on_timeout=True."""
    auditor = DOMAuditor(default_timeout_ms=100)

    # Simula timeout de navegação no Playwright
    with patch("web_visual_auditor.dom_auditor.sync_playwright") as mock_sync_pw:
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        # Importa ou cria a classe de timeout do Playwright
        from web_visual_auditor.dom_auditor import PlaywrightTimeoutError

        mock_page.goto.side_effect = PlaywrightTimeoutError("Navigation timeout of 100ms exceeded")

        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        mock_p.chromium.launch.return_value = mock_browser
        mock_sync_pw.return_value.__enter__.return_value = mock_p

        with pytest.raises(PageNavigationTimeoutError) as exc_info:
            auditor.inspect_url("http://slow-site.test", raise_on_timeout=True)

        assert isinstance(exc_info.value, NavigationTimeoutError)
        assert isinstance(exc_info.value, DOMAuditError)
        assert isinstance(exc_info.value, AuditorError)
        assert "Timeout" in str(exc_info.value)


def test_inspect_url_timeout_falls_back_when_not_raising() -> None:
    """Garante que em timeout de navegação com raise_on_timeout=False o fallback é acionado."""
    auditor = DOMAuditor(default_timeout_ms=100)

    with patch("web_visual_auditor.dom_auditor.sync_playwright") as mock_sync_pw:
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        from web_visual_auditor.dom_auditor import PlaywrightTimeoutError

        mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout")
        # Simula que a página conseguiu reter algum conteúdo no DOM
        mock_page.content.return_value = "<header id='hdr'>Parcial</header>"
        mock_page.evaluate.return_value = [
            {
                "tag_name": "header",
                "element_id": "hdr",
                "classes": [],
                "text_content": "Parcial",
                "is_visible": True,
                "geometry": {"x": 0.0, "y": 0.0, "width": 1280.0, "height": 80.0},
                "selector": "header#hdr",
                "attributes": {"id": "hdr"},
            }
        ]

        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        mock_p.chromium.launch.return_value = mock_browser
        mock_sync_pw.return_value.__enter__.return_value = mock_p

        nodes = auditor.inspect_url("http://partial-page.test", raise_on_timeout=False)
        assert len(nodes) >= 1
        assert nodes[0].element_id == "hdr"


def test_inspect_url_browser_launch_failure_triggers_fallback() -> None:
    """Quando o browser headless falha ao inicializar, o fallback é acionado transparentemente."""
    auditor = DOMAuditor()

    with patch("web_visual_auditor.dom_auditor.sync_playwright") as mock_sync_pw:
        mock_p = MagicMock()
        mock_p.chromium.launch.side_effect = RuntimeError("Chromium binary not found in OS")
        mock_sync_pw.return_value.__enter__.return_value = mock_p

        # Inspeciona arquivo local: deve cair no fallback estrutural sem lançar erro
        nodes = auditor.inspect_url(str(FIXTURE_SAMPLE_PAGE))
        assert len(nodes) >= 6
        header = auditor.find_required_node(nodes, "header")
        assert header.element_id == "main-header"


# ==============================================================================
# 6. Testes de Data URLs, HTML em Memória e Screenshots
# ==============================================================================


def test_inspect_data_url() -> None:
    """Testa inspeção de HTML fornecido diretamente via data URL e HTML em memória."""
    html_raw = "<html><body><button id='action' class='btn'>Confirmar</button></body></html>"
    from urllib.parse import quote

    data_url = f"data:text/html;charset=utf-8,{quote(html_raw)}"

    auditor = DOMAuditor(force_fallback=True)
    # Testa resolução automática de data URL via inspect_url
    nodes_from_url = auditor.inspect_url(data_url)
    assert len(nodes_from_url) == 1
    assert nodes_from_url[0].tag_name == "button"
    assert nodes_from_url[0].element_id == "action"

    # Testa inspect_html diretamente
    nodes_from_html = auditor.inspect_html(html_raw)
    assert len(nodes_from_html) == 1
    assert nodes_from_html[0].element_id == "action"


def test_capture_fullpage_screenshot(tmp_path: Path) -> None:
    """Testa captura de tela de página completa e salvamento de arquivo PNG."""
    auditor = DOMAuditor(force_fallback=True)
    output_png = tmp_path / "test_screenshot.png"

    result_path = auditor.capture_fullpage_screenshot(
        url_or_path=str(FIXTURE_SAMPLE_PAGE),
        output_path=output_png,
    )

    assert Path(result_path).exists()
    assert Path(result_path).stat().st_size > 0
    assert result_path == str(output_png.resolve())


# ==============================================================================
# 7. Testes de Robustez com HTML Incompleto ou Ruidoso
# ==============================================================================


def test_inspect_html_with_malformed_markup() -> None:
    """Valida tolerância a HTML malformado ou tags incompletas."""
    broken_html = "<header id='h'>Sem fechar<article>conteudo<button>ok"
    auditor = DOMAuditor(force_fallback=True)
    nodes = auditor.inspect_html(broken_html)
    assert len(nodes) >= 2
    tags = {n.tag_name for n in nodes}
    assert "header" in tags
    assert "button" in tags
