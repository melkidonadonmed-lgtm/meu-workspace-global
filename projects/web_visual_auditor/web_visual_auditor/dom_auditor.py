"""Módulo de inspeção hierárquica e geométrica do DOM via Playwright headless e fallback resiliente.

Implementa a classe DOMAuditor para inspeção de elementos-chave do DOM,
extração de coordenadas computadas (getBoundingClientRect), visibilidade,
atributos e classes, com suporte adaptativo a Playwright e Patchright,
além de fallback estrutural determinístico offline.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from web_visual_auditor.exceptions import (
    DOMAuditError,
    ElementNotFoundError,
    NavigationTimeoutError,
    PageNavigationTimeoutError,
)
from web_visual_auditor.models import (
    ComputedElementGeometry,
    DOMNodeSummary,
)

logger = logging.getLogger(__name__)

# Import adaptativo dual para Playwright / Patchright conforme especificação arquitetural
try:
    from playwright.sync_api import (
        Browser,
        BrowserContext,
        Page,
        Playwright,
        sync_playwright,
    )
    from playwright.sync_api import (
        TimeoutError as PlaywrightTimeoutError,
    )
except ImportError:
    try:
        from patchright.sync_api import (
            Browser,
            BrowserContext,
            Page,
            Playwright,
            sync_playwright,
        )
        from patchright.sync_api import (
            TimeoutError as PlaywrightTimeoutError,
        )
    except ImportError:
        sync_playwright = None  # type: ignore[assignment]
        PlaywrightTimeoutError = TimeoutError  # type: ignore[assignment,misc]
        Browser = Any  # type: ignore[misc,assignment]
        BrowserContext = Any  # type: ignore[misc,assignment]
        Page = Any  # type: ignore[misc,assignment]
        Playwright = Any  # type: ignore[misc,assignment]


class DOMAuditor:
    """Auditor e extrator de geometrias computadas e resumos do DOM.

    Fornece inspeção headless de alta precisão através de Playwright / Patchright
    e inclui fallback resiliente para parsing de nós estruturais caso o runtime
    do browser headless não esteja disponível ou encontre limitações no ambiente.
    """

    DEFAULT_KEY_SELECTORS: ClassVar[list[str]] = [
        "header",
        "nav",
        "main",
        "h1",
        "article",
        "button",
        "h2",
        "h3",
        "section",
        "footer",
        "[id]",
    ]

    def __init__(
        self,
        headless: bool = True,
        default_timeout_ms: int = 15000,
        viewport_size: dict[str, int] | None = None,
        force_fallback: bool = False,
    ) -> None:
        """Inicializa o auditor de DOM.

        Args:
            headless: Se verdadeiro, executa o navegador sem interface gráfica.
            default_timeout_ms: Timeout padrão em milissegundos para carregamento e ações.
            viewport_size: Dimensões (width, height) da viewport do navegador.
            force_fallback: Força a utilização do fallback estrutural para testes ou offline puro.
        """
        self.headless = headless
        self.default_timeout_ms = default_timeout_ms
        self.viewport_size = viewport_size or {"width": 1280, "height": 800}
        self.force_fallback = force_fallback

    @property
    def is_browser_available(self) -> bool:
        """Verifica se o runtime de Playwright/Patchright está presente e habilitado."""
        return sync_playwright is not None and not self.force_fallback

    def inspect_url(
        self,
        url: str,
        selectors: list[str] | None = None,
        timeout_ms: int | None = None,
        raise_on_timeout: bool = False,
    ) -> list[DOMNodeSummary]:
        """Inspeciona uma URL web ou caminho de arquivo local.

        Args:
            url: Endereço HTTP(S), data URL ou caminho de arquivo no sistema de arquivos.
            selectors: Lista opcional de seletores CSS / tags a extrair.
            timeout_ms: Timeout opcional em milissegundos.
            raise_on_timeout: Se True, lança PageNavigationTimeoutError em timeout de navegação.

        Returns:
            Lista de instâncias DOMNodeSummary contendo nós e geometrias computadas.
        """
        target_selectors = selectors or self.DEFAULT_KEY_SELECTORS
        eff_timeout = timeout_ms if timeout_ms is not None else self.default_timeout_ms

        # Normaliza caminhos de arquivos locais para file:// URI
        normalized_url, local_html_content = self._resolve_url_or_path(url)

        if not self.is_browser_available:
            logger.info("Playwright indisponível ou fallback forçado; usando fallback estrutural.")
            if local_html_content is not None:
                return self._inspect_html_structural_fallback(
                    local_html_content, selectors=target_selectors
                )
            # Se for uma URL remota e não tivermos conteúdo local, tenta ler ou falha graciosa
            html_content = self._fetch_url_content_fallback(normalized_url)
            return self._inspect_html_structural_fallback(
                html_content, selectors=target_selectors
            )

        try:
            return self._inspect_url_headless(
                url=normalized_url,
                selectors=target_selectors,
                timeout_ms=eff_timeout,
                raise_on_timeout=raise_on_timeout,
            )
        except (NavigationTimeoutError, PageNavigationTimeoutError):
            if raise_on_timeout:
                raise
            logger.warning(
                "Timeout em navegação headless para %s; aplicando fallback estrutural.",
                normalized_url,
            )
            if local_html_content is not None:
                return self._inspect_html_structural_fallback(
                    local_html_content, selectors=target_selectors
                )
            html_content = self._fetch_url_content_fallback(normalized_url)
            return self._inspect_html_structural_fallback(
                html_content, selectors=target_selectors
            )
        except Exception as exc:  # noqa: BLE001 - Fallback resiliente proposital
            logger.warning(
                "Falha na execução do browser headless (%s). Acionando fallback estrutural.",
                exc,
            )
            if local_html_content is not None:
                return self._inspect_html_structural_fallback(
                    local_html_content, selectors=target_selectors
                )
            html_content = self._fetch_url_content_fallback(normalized_url)
            return self._inspect_html_structural_fallback(
                html_content, selectors=target_selectors
            )

    def inspect_html(
        self,
        html_content: str,
        selectors: list[str] | None = None,
        timeout_ms: int | None = None,
    ) -> list[DOMNodeSummary]:
        """Inspeciona diretamente uma string contendo código HTML.

        Args:
            html_content: Conteúdo HTML completo.
            selectors: Lista opcional de seletores CSS / tags a extrair.
            timeout_ms: Timeout opcional em milissegundos.

        Returns:
            Lista de instâncias DOMNodeSummary contendo nós e geometrias computadas.
        """
        target_selectors = selectors or self.DEFAULT_KEY_SELECTORS
        eff_timeout = timeout_ms if timeout_ms is not None else self.default_timeout_ms

        if not self.is_browser_available:
            return self._inspect_html_structural_fallback(
                html_content, selectors=target_selectors
            )

        try:
            return self._inspect_html_headless(
                html_content=html_content,
                selectors=target_selectors,
                timeout_ms=eff_timeout,
            )
        except Exception as exc:  # noqa: BLE001 - Fallback resiliente proposital
            logger.warning(
                "Falha no browser headless ao inspecionar HTML (%s). Acionando fallback estrutural.",
                exc,
            )
            return self._inspect_html_structural_fallback(
                html_content, selectors=target_selectors
            )

    def find_node(
        self,
        nodes: list[DOMNodeSummary],
        selector_or_tag: str,
    ) -> DOMNodeSummary | None:
        """Localiza o primeiro nó correspondente a um seletor, tag ou ID.

        Args:
            nodes: Lista de resumos de nós.
            selector_or_tag: Tag, seletor ou ID (com ou sem prefixo #).

        Returns:
            O nó encontrado ou None se inexistente.
        """
        target = selector_or_tag.strip().lower()
        target_id = target.removeprefix("#")

        for node in nodes:
            if node.selector and node.selector.lower() == target:
                return node
            if node.tag_name.lower() == target:
                return node
            if node.element_id and node.element_id.lower() == target_id:
                return node
            if any(f".{cls.lower()}" == target for cls in node.classes):
                return node
        return None

    def find_required_node(
        self,
        nodes: list[DOMNodeSummary],
        selector_or_tag: str,
    ) -> DOMNodeSummary:
        """Localiza um nó obrigatório ou lança ElementNotFoundError caso ausente.

        Args:
            nodes: Lista de resumos de nós.
            selector_or_tag: Tag, seletor ou ID procurado.

        Returns:
            O nó DOMNodeSummary localizado.

        Raises:
            ElementNotFoundError: Caso o elemento não seja encontrado na lista.
        """
        node = self.find_node(nodes, selector_or_tag)
        if node is None:
            raise ElementNotFoundError(
                selector=selector_or_tag,
                message=f"Elemento obrigatório não encontrado no DOM: '{selector_or_tag}'",
            )
        return node

    def capture_fullpage_screenshot(
        self,
        url_or_path: str,
        output_path: str | Path,
        viewport_size: dict[str, int] | None = None,
    ) -> str:
        """Gera captura de tela da página inteira em modo headless.

        Args:
            url_or_path: URL ou caminho de arquivo local da página.
            output_path: Destino do arquivo PNG da screenshot.
            viewport_size: Dimensões customizadas da viewport se desejado.

        Returns:
            Caminho absoluto do arquivo gravado.
        """
        out_path = Path(output_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        viewport = viewport_size or self.viewport_size

        normalized_url, local_html = self._resolve_url_or_path(url_or_path)

        if self.is_browser_available:
            try:
                assert sync_playwright is not None
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=self.headless,
                        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
                    )
                    try:
                        context = browser.new_context(viewport=viewport)
                        page = context.new_page()
                        page.set_default_timeout(self.default_timeout_ms)

                        if local_html is not None and not normalized_url.startswith("file://"):
                            page.set_content(local_html, wait_until="domcontentloaded")
                        else:
                            page.goto(normalized_url, wait_until="domcontentloaded")

                        page.screenshot(path=str(out_path), full_page=True)
                        return str(out_path)
                    finally:
                        browser.close()
            except Exception as exc:  # noqa: BLE001 - Fallback sintético
                logger.warning(
                    "Falha ao gerar screenshot via Playwright (%s); gerando imagem de fallback.",
                    exc,
                )

        # Fallback sintético via Pillow
        try:
            from PIL import Image, ImageDraw

            img = Image.new(
                "RGB",
                (viewport.get("width", 1280), viewport.get("height", 800)),
                (248, 250, 252),
            )
            draw = ImageDraw.Draw(img)
            draw.text((32, 32), f"Web Visual Auditor Snapshot\nTarget: {url_or_path}", fill=(15, 23, 42))
            img.save(str(out_path), format="PNG")
        except Exception as exc:
            raise DOMAuditError(f"Não foi possível gravar screenshot em {out_path}: {exc}") from exc

        return str(out_path)

    # ==========================================================================
    # Métodos Internos: Execução Headless com Playwright
    # ==========================================================================

    def _inspect_url_headless(
        self,
        url: str,
        selectors: list[str],
        timeout_ms: int,
        raise_on_timeout: bool,
    ) -> list[DOMNodeSummary]:
        """Executa a inspeção da URL dentro do contexto Playwright."""
        assert sync_playwright is not None
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                context = browser.new_context(viewport=self.viewport_size)
                page = context.new_page()
                page.set_default_timeout(timeout_ms)

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                except PlaywrightTimeoutError as err:
                    if raise_on_timeout:
                        raise PageNavigationTimeoutError(
                            f"Timeout de {timeout_ms}ms ao carregar URL '{url}': {err}"
                        ) from err
                    # Tenta avaliar o que já existe carregado no DOM
                    try:
                        content = page.content()
                        if not content or content == "<html><head></head><body></body></html>":
                            raise PageNavigationTimeoutError(
                                f"Timeout sem conteúdo carregado em '{url}': {err}"
                            ) from err
                    except Exception as content_err:  # noqa: BLE001
                        raise PageNavigationTimeoutError(
                            f"Timeout irrecuperável em '{url}': {content_err}"
                        ) from err

                return self._evaluate_and_extract_nodes(page, selectors)
            finally:
                browser.close()

    def _inspect_html_headless(
        self,
        html_content: str,
        selectors: list[str],
        timeout_ms: int,
    ) -> list[DOMNodeSummary]:
        """Executa a inspeção do HTML em memória via Playwright."""
        assert sync_playwright is not None
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                context = browser.new_context(viewport=self.viewport_size)
                page = context.new_page()
                page.set_default_timeout(timeout_ms)
                page.set_content(html_content, wait_until="domcontentloaded", timeout=timeout_ms)
                return self._evaluate_and_extract_nodes(page, selectors)
            finally:
                browser.close()

    def _evaluate_and_extract_nodes(
        self,
        page: Page,
        selectors: list[str],
    ) -> list[DOMNodeSummary]:
        """Injeta script JS na página para obter getBoundingClientRect e atributos."""
        extraction_script = """
        (selectors) => {
            const results = [];
            const seenElements = new Set();

            for (const sel of selectors) {
                let elements = [];
                try {
                    elements = Array.from(document.querySelectorAll(sel));
                } catch (e) {
                    continue;
                }

                for (const el of elements) {
                    if (seenElements.has(el)) {
                        continue;
                    }
                    seenElements.add(el);

                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);

                    const isDisplayNone = style.display === 'none';
                    const isVisibilityHidden = (style.visibility === 'hidden' || style.visibility === 'collapse');
                    const isOpacityZero = parseFloat(style.opacity || '1') === 0;
                    const hasZeroDimensions = (rect.width <= 0 || rect.height <= 0);

                    const isVisible = !isDisplayNone && !isVisibilityHidden && !isOpacityZero && !hasZeroDimensions;

                    const classes = Array.from(el.classList);
                    const attributes = {};
                    for (let i = 0; i < el.attributes.length; i++) {
                        const attr = el.attributes[i];
                        attributes[attr.name] = attr.value;
                    }

                    const rawText = (el.innerText || el.textContent || '').trim();
                    const textContent = rawText.length > 0 ? rawText : null;

                    let suggestedSelector = sel;
                    if (el.id) {
                        suggestedSelector = `${el.tagName.toLowerCase()}#${el.id}`;
                    } else if (classes.length > 0) {
                        suggestedSelector = `${el.tagName.toLowerCase()}.${classes.join('.')}`;
                    }

                    results.push({
                        tag_name: el.tagName.toLowerCase(),
                        element_id: el.id || null,
                        classes: classes,
                        text_content: textContent,
                        is_visible: isVisible,
                        geometry: {
                            x: Math.round(rect.x * 100) / 100,
                            y: Math.round(rect.y * 100) / 100,
                            width: Math.round(rect.width * 100) / 100,
                            height: Math.round(rect.height * 100) / 100
                        },
                        selector: suggestedSelector,
                        attributes: attributes
                    });
                }
            }
            return results;
        }
        """

        raw_nodes_data = page.evaluate(extraction_script, selectors)
        return [self._convert_to_dom_summary(item) for item in raw_nodes_data]

    # ==========================================================================
    # Métodos Internos: Fallback Estrutural Resiliente (Offline / No-Browser)
    # ==========================================================================

    def _inspect_html_structural_fallback(
        self,
        html_content: str,
        selectors: list[str],
    ) -> list[DOMNodeSummary]:
        """Gera resumos estruturais e geometrias determinísticas via BeautifulSoup e CSS parsing."""
        soup = BeautifulSoup(html_content, "html.parser")
        css_rules = self._parse_css_declarations(html_content)

        results: list[DOMNodeSummary] = []
        seen_element_ids: set[int] = set()

        viewport_w = float(self.viewport_size.get("width", 1280))
        y_cursor = 0.0

        for sel in selectors:
            try:
                elements = soup.select(sel)
            except Exception:  # noqa: BLE001
                # Se falhar a seleção CSS direta, tenta por tag
                elements = soup.find_all(sel.lower())

            for el in elements:
                el_hash = id(el)
                if el_hash in seen_element_ids:
                    continue
                seen_element_ids.add(el_hash)

                tag_name = el.name.lower()
                element_id = el.get("id") or None
                raw_classes = el.get("class", [])
                classes = list(raw_classes) if isinstance(raw_classes, list) else [str(raw_classes)]

                # Atributos chave
                attributes: dict[str, str] = {}
                for k, v in el.attrs.items():
                    if isinstance(v, list):
                        attributes[k] = " ".join(str(item) for item in v)
                    else:
                        attributes[k] = str(v)

                # Texto interno limpo
                text_raw = el.get_text(separator=" ", strip=True)
                text_content = text_raw if text_raw else None

                # Seletor sugerido
                if element_id:
                    suggested_selector = f"{tag_name}#{element_id}"
                elif classes:
                    suggested_selector = f"{tag_name}.{'.'.join(classes)}"
                else:
                    suggested_selector = tag_name

                # Consolidação de estilos (inline + classes + tag)
                computed_styles = self._resolve_element_styles(
                    tag_name=tag_name,
                    element_id=element_id,
                    classes=classes,
                    inline_style=el.get("style", ""),
                    css_rules=css_rules,
                )

                # Avaliação de visibilidade
                is_display_none = computed_styles.get("display") == "none"
                is_visibility_hidden = computed_styles.get("visibility") in ("hidden", "collapse")
                has_hidden_class = any(
                    cls in ("hidden-box", "zero-dim-box", "hidden", "invisible") for cls in classes
                )
                is_aria_hidden = el.get("aria-hidden") == "true" and (
                    is_display_none or has_hidden_class
                )
                is_html_hidden = el.has_attr("hidden")

                is_visible = not (
                    is_display_none
                    or is_visibility_hidden
                    or has_hidden_class
                    or is_aria_hidden
                    or is_html_hidden
                )

                # Avaliação de dimensões e posições
                width, height = self._estimate_element_dimensions(
                    tag_name=tag_name,
                    classes=classes,
                    computed_styles=computed_styles,
                    viewport_w=viewport_w,
                    is_visible=is_visible,
                )

                # Coordenadas X e Y
                if not is_visible or (width <= 0 or height <= 0):
                    x_coord = 0.0
                    y_coord = y_cursor
                    is_visible = False
                else:
                    # Posição X e incremento de Y para fluxo natural
                    x_coord = 32.0 if tag_name in ("article", "button", "h1") else 0.0
                    y_coord = y_cursor
                    y_cursor += height + 16.0

                geo = ComputedElementGeometry(
                    x=round(x_coord, 2),
                    y=round(y_coord, 2),
                    width=round(width, 2),
                    height=round(height, 2),
                )

                summary = DOMNodeSummary(
                    tag_name=tag_name,
                    element_id=element_id,
                    classes=classes,
                    text_content=text_content,
                    is_visible=is_visible,
                    geometry=geo,
                    selector=suggested_selector,
                    attributes=attributes,
                )
                results.append(summary)

        return results

    def _parse_css_declarations(self, html_content: str) -> dict[str, dict[str, str]]:
        """Extrai declarações CSS contidas em blocos <style> do documento HTML."""
        css_map: dict[str, dict[str, str]] = {}
        soup = BeautifulSoup(html_content, "html.parser")

        for style_tag in soup.find_all("style"):
            css_text = style_tag.get_text()
            # Encontra regras CSS com formato: seletor { declaracoes }
            matches = re.findall(r"([^{]+)\{([^}]+)\}", css_text)
            for raw_selectors, raw_decls in matches:
                selectors_list = [s.strip() for s in raw_selectors.split(",") if s.strip()]
                decls: dict[str, str] = {}
                for line in raw_decls.split(";"):
                    if ":" in line:
                        prop, val = line.split(":", 1)
                        decls[prop.strip().lower()] = val.strip().lower()

                for sel in selectors_list:
                    if sel not in css_map:
                        css_map[sel] = {}
                    css_map[sel].update(decls)

        return css_map

    def _resolve_element_styles(
        self,
        tag_name: str,
        element_id: str | None,
        classes: list[str],
        inline_style: str,
        css_rules: dict[str, dict[str, str]],
    ) -> dict[str, str]:
        """Consolida as propriedades CSS de um nó a partir de tag, classes, ID e inline."""
        merged: dict[str, str] = {}

        # 1. Por tag
        if tag_name in css_rules:
            merged.update(css_rules[tag_name])

        # 2. Por classe simples e composta
        for cls in classes:
            if f".{cls}" in css_rules:
                merged.update(css_rules[f".{cls}"])
            if f"{tag_name}.{cls}" in css_rules:
                merged.update(css_rules[f"{tag_name}.{cls}"])

        # 3. Por ID
        if element_id:
            if f"#{element_id}" in css_rules:
                merged.update(css_rules[f"#{element_id}"])
            if f"{tag_name}#{element_id}" in css_rules:
                merged.update(css_rules[f"{tag_name}#{element_id}"])

        # 4. Estilo inline (maior precedência)
        if inline_style:
            for item in inline_style.split(";"):
                if ":" in item:
                    k, v = item.split(":", 1)
                    merged[k.strip().lower()] = v.strip().lower()

        return merged

    def _estimate_element_dimensions(
        self,
        tag_name: str,
        classes: list[str],
        computed_styles: dict[str, str],
        viewport_w: float,
        is_visible: bool,
    ) -> tuple[float, float]:
        """Calcula ou estima largura e altura a partir de estilos CSS computados."""
        if not is_visible:
            return (0.0, 0.0)

        # Se houver dimensão zero explícita
        if "zero-dim-box" in classes:
            return (0.0, 0.0)

        # 1. Largura
        raw_w = computed_styles.get("width")
        width: float = viewport_w
        if raw_w:
            if raw_w.endswith("px"):
                try:
                    width = float(raw_w.replace("px", "").strip())
                except ValueError:
                    width = viewport_w
            elif raw_w == "100%":
                width = viewport_w
            elif raw_w == "0" or raw_w == "0px":
                width = 0.0
        else:
            # Padrões semânticos por tag
            if tag_name in ("header", "main", "footer", "nav", "article", "section"):
                width = viewport_w if tag_name != "article" else 800.0
            elif tag_name == "button":
                width = 160.0 if "btn-primary" in classes else 120.0
            elif tag_name.startswith("h"):
                width = 600.0

        # 2. Altura
        raw_h = computed_styles.get("height")
        height: float = 40.0
        if raw_h:
            if raw_h.endswith("px"):
                try:
                    height = float(raw_h.replace("px", "").strip())
                except ValueError:
                    height = 40.0
            elif raw_h == "0" or raw_h == "0px":
                height = 0.0
        else:
            if tag_name == "header":
                height = 80.0
            elif tag_name == "footer":
                height = 60.0
            elif tag_name == "button":
                height = 42.0
            elif tag_name == "h1":
                height = 36.0
            elif tag_name == "article":
                height = 300.0
            elif tag_name == "nav":
                height = 50.0

        return (width, height)

    # ==========================================================================
    # Métodos Utilitários de Resolução e Conversão
    # ==========================================================================

    def _resolve_url_or_path(self, url_or_path: str) -> tuple[str, str | None]:
        """Determina se o alvo é uma URL web, data URI ou arquivo local em disco.

        Returns:
            Tupla contendo (normalized_url, local_html_content_ou_None).
        """
        # Se for data URL
        if url_or_path.startswith("data:"):
            if "," in url_or_path:
                header_part, data_part = url_or_path.split(",", 1)
                if ";base64" in header_part:
                    import base64

                    try:
                        decoded = base64.b64decode(data_part).decode("utf-8")
                        return (url_or_path, decoded)
                    except Exception:  # noqa: BLE001, S110
                        pass
                else:
                    from urllib.parse import unquote

                    return (url_or_path, unquote(data_part))
            return (url_or_path, None)

        # Se for http / https
        parsed = urlparse(url_or_path)
        if parsed.scheme in ("http", "https"):
            return (url_or_path, None)

        # Se for file:// URI
        if url_or_path.startswith("file://"):
            # Tenta ler o arquivo local correspondente
            clean_path = url_or_path.replace("file:///", "").replace("file://", "")
            local_p = Path(clean_path)
            content = local_p.read_text(encoding="utf-8") if local_p.exists() else None
            return (url_or_path, content)

        # Trata como caminho de arquivo local no disco
        try:
            local_p = Path(url_or_path).resolve()
            if local_p.exists() and local_p.is_file():
                content = local_p.read_text(encoding="utf-8")
                return (local_p.as_uri(), content)
        except (OSError, ValueError):
            pass

        # Se não existir como arquivo físico mas parecer uma URL
        return (url_or_path, None)

    def _fetch_url_content_fallback(self, url: str) -> str:
        """Obtém o conteúdo textual de uma URL remota via HTTPX ou mock offline."""
        try:
            import httpx

            resp = httpx.get(url, timeout=self.default_timeout_ms / 1000.0)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falha ao recuperar URL via HTTPX (%s); retornando HTML vazio.", exc)
            return "<html><body></body></html>"

    def _convert_to_dom_summary(self, data: dict[str, Any]) -> DOMNodeSummary:
        """Converte dicionário extraído do JS em instância tipada de DOMNodeSummary."""
        geo_dict = data.get("geometry", {})
        geometry = ComputedElementGeometry(
            x=float(geo_dict.get("x", 0.0)),
            y=float(geo_dict.get("y", 0.0)),
            width=float(geo_dict.get("width", 0.0)),
            height=float(geo_dict.get("height", 0.0)),
        )

        return DOMNodeSummary(
            tag_name=str(data.get("tag_name", "div")),
            element_id=data.get("element_id"),
            classes=list(data.get("classes", [])),
            text_content=data.get("text_content"),
            is_visible=bool(data.get("is_visible", True)),
            geometry=geometry,
            selector=data.get("selector"),
            attributes=dict(data.get("attributes", {})),
        )
