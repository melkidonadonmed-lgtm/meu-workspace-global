"""Módulo de auditoria granular por micro-componentes de design systems.

Permite isolar componentes individuais delimitados por seletores CSS específicos
(botões, cards, modais, headers), capturando a área recortada via element.screenshot()
ou recorte por bounding box e executando comparações diferenciais independentes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from web_visual_auditor.exceptions import (
    ComponentAuditError,
    ElementNotFoundError,
)
from web_visual_auditor.models import (
    ComponentDiffReport,
    ComponentSnapshot,
    ComputedElementGeometry,
)
from web_visual_auditor.visual_regression import VisualRegressionAuditor

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment]
    HAS_PIL = False

try:
    from playwright.async_api import async_playwright
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:  # pragma: no cover
    HAS_PLAYWRIGHT = False


def sanitize_selector(selector: str) -> str:
    """Higieniza um seletor CSS para compor nomes de arquivos seguros no sistema operacional.

    Exemplos:
        'button.btn-primary' -> 'button_btn-primary'
        '#main-header > nav' -> 'main-header_nav'
    """
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", selector.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "component"


class ComponentAuditor:
    """Auditor granular para isolamento e comparação de micro-componentes."""

    def __init__(
        self,
        visual_engine: VisualRegressionAuditor | None = None,
        dom_auditor: Any | None = None,
        browser_timeout_ms: int = 15000,
        headless: bool = True,
    ) -> None:
        """Inicializa o auditor de componentes.

        Args:
            visual_engine: Instância do motor de regressão visual para comparar snapshots.
            dom_auditor: Instância opcional de DOMAuditor para inspeção estrutural.
            browser_timeout_ms: Timeout em milissegundos para operações de página.
            headless: Se o navegador Playwright deve rodar em modo headless.
        """
        self.visual_engine = visual_engine or VisualRegressionAuditor()
        self.dom_auditor = dom_auditor
        self.browser_timeout_ms = browser_timeout_ms
        self.headless = headless

    def capture_component_from_image(
        self,
        fullpage_image: str | Path | Any,
        selector: str,
        bounding_box: tuple[int, int, int, int] | ComputedElementGeometry,
        output_path: str | Path,
    ) -> ComponentSnapshot:
        """Recorta um componente a partir de uma captura de tela existente e de suas coordenadas.

        Atua como fallback gracioso quando o navegador não puder executar screenshots diretos.

        Args:
            fullpage_image: Caminho ou objeto PIL.Image da tela completa.
            selector: Seletor CSS associado ao componente.
            bounding_box: Coordenadas (x, y, width, height) ou ComputedElementGeometry.
            output_path: Caminho no disco para gravação do snapshot recortado.

        Returns:
            ComponentSnapshot contendo o arquivo gravado e metadados.
        """
        dest_path = Path(output_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(bounding_box, ComputedElementGeometry):
            x = int(bounding_box.x)
            y = int(bounding_box.y)
            w = int(bounding_box.width)
            h = int(bounding_box.height)
            geom = bounding_box
        else:
            x, y, w, h = (int(v) for v in bounding_box)
            geom = ComputedElementGeometry(x=float(x), y=float(y), width=float(w), height=float(h))

        if w <= 0 or h <= 0:
            raise ComponentAuditError(
                f"Dimensões inválidas para recorte do componente '{selector}': {w}x{h}"
            )

        if not HAS_PIL:
            raise ComponentAuditError(
                "Pillow (PIL) é obrigatório para execução de recorte por bounding box."
            )

        if isinstance(fullpage_image, (str, Path)):
            src_img = Image.open(fullpage_image)
        else:
            src_img = fullpage_image

        crop_box = (x, y, x + w, y + h)
        cropped = src_img.crop(crop_box)
        cropped.save(dest_path, format="PNG")

        return ComponentSnapshot(
            selector=selector,
            dimensions=(w, h),
            screenshot_path=str(dest_path),
            geometry=geom,
            is_visible=True,
        )

    def capture_component(
        self,
        url_or_html: str,
        selector: str,
        output_path: str | Path | None = None,
    ) -> ComponentSnapshot:
        """Isola um componente e gera seu snapshot.

        Se output_path não for fornecido, compõe automaticamente no formato:
        'component_<selector_sanitized>.png'.
        """
        if output_path is None:
            safe_name = sanitize_selector(selector)
            output_path = f"component_{safe_name}.png"
        return self.capture_component_snapshot(url_or_html, selector, output_path)

    def capture_component_snapshot(
        self,
        url_or_path: str,
        selector: str,
        output_path: str | Path,
    ) -> ComponentSnapshot:
        """Captura síncrona do snapshot de um componente via Playwright."""
        dest_path = Path(output_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if not HAS_PLAYWRIGHT:
            raise ComponentAuditError(
                "Playwright não está instalado. Instale playwright para capturar componentes."
            )

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                try:
                    page = browser.new_page()
                    self._navigate_page_sync(page, url_or_path)

                    locator = page.locator(selector).first
                    if locator.count() == 0:
                        raise ElementNotFoundError(
                            selector=selector,
                            message=f"Componente não encontrado para o seletor CSS: '{selector}'",
                        )

                    is_visible = locator.is_visible()
                    box = locator.bounding_box()

                    # Obter metadados
                    try:
                        tag_name = page.evaluate(
                            "el => el.tagName ? el.tagName.toLowerCase() : null",
                            locator.element_handle(),
                        )
                    except Exception:  # noqa: BLE001
                        tag_name = None

                    try:
                        inner_text = locator.inner_text(timeout=2000)
                    except Exception:  # noqa: BLE001
                        inner_text = None

                    locator.screenshot(path=str(dest_path))

                    if HAS_PIL and dest_path.exists():
                        with Image.open(dest_path) as img:
                            dims = img.size
                    elif box:
                        dims = (int(box["width"]), int(box["height"]))
                    else:
                        dims = (0, 0)

                    geom = None
                    if box:
                        geom = ComputedElementGeometry(
                            x=float(box["x"]),
                            y=float(box["y"]),
                            width=float(box["width"]),
                            height=float(box["height"]),
                        )

                    return ComponentSnapshot(
                        selector=selector,
                        dimensions=dims,
                        screenshot_path=str(dest_path),
                        geometry=geom,
                        is_visible=is_visible,
                        tag_name=tag_name,
                        inner_text=inner_text,
                    )
                finally:
                    browser.close()
        except ElementNotFoundError:
            raise
        except Exception as exc:
            raise ComponentAuditError(
                f"Erro durante a captura do componente '{selector}': {exc}"
            ) from exc

    async def capture_component_snapshot_async(
        self,
        url_or_path: str,
        selector: str,
        output_path: str | Path,
    ) -> ComponentSnapshot:
        """Captura assíncrona do snapshot de um componente via Playwright async API."""
        dest_path = Path(output_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if not HAS_PLAYWRIGHT:
            raise ComponentAuditError("Playwright não está instalado.")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                try:
                    page = await browser.new_page()
                    await self._navigate_page_async(page, url_or_path)

                    locator = page.locator(selector).first
                    count = await locator.count()
                    if count == 0:
                        raise ElementNotFoundError(
                            selector=selector,
                            message=f"Componente não encontrado para o seletor CSS: '{selector}'",
                        )

                    is_visible = await locator.is_visible()
                    box = await locator.bounding_box()

                    try:
                        handle = await locator.element_handle()
                        tag_name = await page.evaluate(
                            "el => el.tagName ? el.tagName.toLowerCase() : null",
                            handle,
                        )
                    except Exception:  # noqa: BLE001
                        tag_name = None

                    try:
                        inner_text = await locator.inner_text(timeout=2000)
                    except Exception:  # noqa: BLE001
                        inner_text = None

                    await locator.screenshot(path=str(dest_path))

                    if HAS_PIL and dest_path.exists():
                        with Image.open(dest_path) as img:
                            dims = img.size
                    elif box:
                        dims = (int(box["width"]), int(box["height"]))
                    else:
                        dims = (0, 0)

                    geom = None
                    if box:
                        geom = ComputedElementGeometry(
                            x=float(box["x"]),
                            y=float(box["y"]),
                            width=float(box["width"]),
                            height=float(box["height"]),
                        )

                    return ComponentSnapshot(
                        selector=selector,
                        dimensions=dims,
                        screenshot_path=str(dest_path),
                        geometry=geom,
                        is_visible=is_visible,
                        tag_name=tag_name,
                        inner_text=inner_text,
                    )
                finally:
                    await browser.close()
        except ElementNotFoundError:
            raise
        except Exception as exc:
            raise ComponentAuditError(
                f"Erro durante a captura assíncrona do componente '{selector}': {exc}"
            ) from exc

    @staticmethod
    def _is_local_file(url_or_path: str) -> bool:
        """Verifica de forma resiliente se url_or_path é um arquivo no disco."""
        try:
            return Path(url_or_path).is_file()
        except (OSError, ValueError):
            return False

    def _navigate_page_sync(self, page: Any, url_or_path: str) -> None:
        """Navega ou injeta conteúdo HTML na página síncrona."""
        url_lower = url_or_path.strip().lower()
        if url_lower.startswith(("http://", "https://", "file://", "data:")):
            page.goto(url_or_path, wait_until="domcontentloaded", timeout=self.browser_timeout_ms)
        elif self._is_local_file(url_or_path):
            abs_uri = Path(url_or_path).resolve().as_uri()
            page.goto(abs_uri, wait_until="domcontentloaded", timeout=self.browser_timeout_ms)
        else:
            page.set_content(
                url_or_path,
                wait_until="domcontentloaded",
                timeout=self.browser_timeout_ms,
            )

    async def _navigate_page_async(self, page: Any, url_or_path: str) -> None:
        """Navega ou injeta conteúdo HTML na página assíncrona."""
        url_lower = url_or_path.strip().lower()
        if url_lower.startswith(("http://", "https://", "file://", "data:")):
            await page.goto(
                url_or_path,
                wait_until="domcontentloaded",
                timeout=self.browser_timeout_ms,
            )
        elif self._is_local_file(url_or_path):
            abs_uri = Path(url_or_path).resolve().as_uri()
            await page.goto(
                abs_uri,
                wait_until="domcontentloaded",
                timeout=self.browser_timeout_ms,
            )
        else:
            await page.set_content(
                url_or_path,
                wait_until="domcontentloaded",
                timeout=self.browser_timeout_ms,
            )

    def compare_component_snapshots(
        self,
        baseline_snapshot: ComponentSnapshot | None,
        current_snapshot: ComponentSnapshot | None,
        selector: str | None = None,
        diff_output_path: str | Path | None = None,
    ) -> ComponentDiffReport:
        """Compara dois snapshots de componente e gera o relatório diferencial.

        Gera máscara diferencial nomeada 'diff_<selector_sanitized>.png' destacando
        alterações em vermelho puro (#FF0000).
        """
        sel = selector
        if sel is None:
            if baseline_snapshot:
                sel = baseline_snapshot.selector
            elif current_snapshot:
                sel = current_snapshot.selector
            else:
                sel = "unknown_component"

        # Caso componente não exista na baseline
        if baseline_snapshot is None and current_snapshot is not None:
            return ComponentDiffReport(
                selector=sel,
                baseline_dimensions=None,
                current_dimensions=current_snapshot.dimensions,
                diff_result=None,
                baseline_snapshot=None,
                current_snapshot=current_snapshot,
                status="missing_in_baseline",
                geometry_changed=True,
            )

        # Caso componente tenha sido removido na versão atual
        if current_snapshot is None and baseline_snapshot is not None:
            return ComponentDiffReport(
                selector=sel,
                baseline_dimensions=baseline_snapshot.dimensions,
                current_dimensions=None,
                diff_result=None,
                baseline_snapshot=baseline_snapshot,
                current_snapshot=None,
                status="missing_in_current",
                geometry_changed=True,
            )

        if baseline_snapshot is None and current_snapshot is None:
            return ComponentDiffReport(
                selector=sel,
                status="missing_in_both",
                geometry_changed=False,
            )

        assert baseline_snapshot is not None
        assert current_snapshot is not None

        # Validação de alteração dimensional ou espacial
        geometry_changed = False
        if baseline_snapshot.dimensions != current_snapshot.dimensions:
            geometry_changed = True

        if (
            baseline_snapshot.geometry
            and current_snapshot.geometry
            and baseline_snapshot.geometry.as_tuple != current_snapshot.geometry.as_tuple
        ):
            geometry_changed = True

        # Se as dimensões forem iguais, realiza a comparação visual pixel a pixel
        if baseline_snapshot.dimensions == current_snapshot.dimensions:
            if diff_output_path is None:
                safe_name = sanitize_selector(sel)
                diff_output_path = f"diff_{safe_name}.png"

            diff_res = self.visual_engine.compare_images(
                baseline_img=baseline_snapshot.screenshot_path,
                current_img=current_snapshot.screenshot_path,
                diff_output_path=diff_output_path,
            )

            status = "diverged" if diff_res.has_divergence else "matched"

            return ComponentDiffReport(
                selector=sel,
                baseline_dimensions=baseline_snapshot.dimensions,
                current_dimensions=current_snapshot.dimensions,
                diff_result=diff_res,
                baseline_snapshot=baseline_snapshot,
                current_snapshot=current_snapshot,
                status=status,
                geometry_changed=geometry_changed,
            )

        # Caso as dimensões sejam divergentes
        return ComponentDiffReport(
            selector=sel,
            baseline_dimensions=baseline_snapshot.dimensions,
            current_dimensions=current_snapshot.dimensions,
            diff_result=None,
            baseline_snapshot=baseline_snapshot,
            current_snapshot=current_snapshot,
            status="diverged",
            geometry_changed=True,
        )

    def audit_component(
        self,
        baseline_url_or_html: str,
        current_url_or_html: str,
        selector: str,
        diff_output_dir: str | Path = ".",
    ) -> ComponentDiffReport:
        """Audita um micro-componente isolado entre duas versões da interface."""
        out_dir = Path(diff_output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        safe_sel = sanitize_selector(selector)
        base_path = out_dir / f"baseline_{safe_sel}.png"
        curr_path = out_dir / f"current_{safe_sel}.png"
        diff_path = out_dir / f"diff_{safe_sel}.png"

        base_snap: ComponentSnapshot | None = None
        try:
            base_snap = self.capture_component_snapshot(
                baseline_url_or_html,
                selector,
                base_path,
            )
        except ElementNotFoundError:
            base_snap = None

        curr_snap: ComponentSnapshot | None = None
        try:
            curr_snap = self.capture_component_snapshot(
                current_url_or_html,
                selector,
                curr_path,
            )
        except ElementNotFoundError:
            curr_snap = None

        return self.compare_component_snapshots(
            baseline_snapshot=base_snap,
            current_snapshot=curr_snap,
            selector=selector,
            diff_output_path=diff_path,
        )

    def audit_components(
        self,
        baseline_url: str,
        current_url: str,
        selectors: list[str],
        output_dir: str | Path = ".",
    ) -> list[ComponentDiffReport]:
        """Audita síncronamente múltiplos seletores CSS."""
        reports: list[ComponentDiffReport] = []
        for sel in selectors:
            report = self.audit_component(
                baseline_url_or_html=baseline_url,
                current_url_or_html=current_url,
                selector=sel,
                diff_output_dir=output_dir,
            )
            reports.append(report)
        return reports

    async def audit_components_async(
        self,
        baseline_url: str,
        current_url: str,
        selectors: list[str],
        output_dir: str | Path = ".",
    ) -> list[ComponentDiffReport]:
        """Audita assincronamente múltiplos seletores CSS."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        reports: list[ComponentDiffReport] = []
        for sel in selectors:
            safe_sel = sanitize_selector(sel)
            base_path = out_dir / f"baseline_{safe_sel}.png"
            curr_path = out_dir / f"current_{safe_sel}.png"
            diff_path = out_dir / f"diff_{safe_sel}.png"

            base_snap: ComponentSnapshot | None = None
            try:
                base_snap = await self.capture_component_snapshot_async(
                    baseline_url,
                    sel,
                    base_path,
                )
            except ElementNotFoundError:
                base_snap = None

            curr_snap: ComponentSnapshot | None = None
            try:
                curr_snap = await self.capture_component_snapshot_async(
                    current_url,
                    sel,
                    curr_path,
                )
            except ElementNotFoundError:
                curr_snap = None

            report = self.compare_component_snapshots(
                baseline_snapshot=base_snap,
                current_snapshot=curr_snap,
                selector=sel,
                diff_output_path=diff_path,
            )
            reports.append(report)

        return reports
