"""Módulo orquestrador central da suíte Web Visual Auditor.

Integra de ponta a ponta os quatro pilares modulares:
1. Pesquisa Web e Extração Semântica (WebResearcher)
2. Inspeção Estrutural e Geométrica do DOM (DOMAuditor)
3. Auditoria Visual Diferencial Pixel a Pixel (VisualRegressionAuditor)
4. Auditoria Granular de Micro-Componentes de Design System (ComponentAuditor)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from web_visual_auditor.component_auditor import ComponentAuditor
from web_visual_auditor.dom_auditor import DOMAuditor
from web_visual_auditor.models import (
    ComponentDiffReport,
    DOMNodeSummary,
    SourceReference,
    SuiteAuditReport,
    VisualDiffResult,
)
from web_visual_auditor.researcher import WebResearcher
from web_visual_auditor.visual_regression import VisualRegressionAuditor

logger = logging.getLogger(__name__)


class SuiteConfig(BaseModel):
    """Configuração declarativa para execução integrada da suíte de auditoria."""

    model_config = ConfigDict(extra="ignore")

    baseline_url: str = Field(
        default="",
        description="URL, caminho de arquivo ou string da baseline",
    )
    current_url: str = Field(
        default="",
        description="URL, caminho de arquivo ou string da versão sob teste",
    )
    component_selectors: list[str] = Field(
        default_factory=list,
        description="Lista de seletores CSS para isolamento e auditoria de micro-componentes",
    )
    search_query: str | None = Field(
        default=None,
        description="Termo opcional de busca para pesquisa semântica integrada",
    )
    search_limit: int = Field(
        default=5,
        ge=1,
        description="Quantidade máxima de referências na pesquisa semântica",
    )
    tolerance: int = Field(
        default=15,
        ge=0,
        le=255,
        description="Limiar de tolerância de antialiasing por canal RGB (padrão: 15)",
    )
    output_dir: str = Field(
        default="audit_reports",
        description="Diretório destino para salvar screenshots, máscaras diferenciais e relatórios",
    )
    diff_fullpage_name: str = Field(
        default="diff_result.png",
        description="Nome do arquivo da máscara diferencial de tela cheia",
    )
    capture_fullpage: bool = Field(
        default=True,
        description="Se verdadeiro, realiza a comparação visual de página inteira",
    )
    save_report_json: bool = Field(
        default=False,
        description="Se verdadeiro, persiste suite_report.json automaticamente no output_dir",
    )


def _is_image_path(candidate: str | Path | Any) -> bool:
    """Verifica se o alvo fornecido aponta para um arquivo de imagem existente."""
    if not isinstance(candidate, (str, Path)):
        return False
    path_obj = Path(candidate)
    if not path_obj.exists() or not path_obj.is_file():
        return False
    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".ppm", ".tiff"}
    return path_obj.suffix.lower() in image_extensions


def _looks_like_raw_html(candidate: str) -> bool:
    """Identifica se uma string contém marcação HTML bruta ao invés de URL ou caminho."""
    if not isinstance(candidate, str):
        return False
    stripped = candidate.strip()
    if stripped.startswith(("http://", "https://", "file://", "data:")):
        return False
    try:
        if Path(stripped).exists():
            return False
    except (OSError, ValueError):
        pass

    # Verifica tags comuns de marcação
    lower_s = stripped.lower()
    return (
        "<html" in lower_s
        or "<!doctype" in lower_s
        or "<body" in lower_s
        or "<div" in lower_s
        or "<header" in lower_s
        or "<main" in lower_s
        or "<button" in lower_s
        or ("<" in stripped and ">" in stripped)
    )


class WebVisualAuditorSuite:
    """Classe orquestradora unificada para inspeção e auditoria visual."""

    def __init__(
        self,
        researcher: WebResearcher | None = None,
        dom_auditor: DOMAuditor | None = None,
        visual_engine: VisualRegressionAuditor | None = None,
        component_auditor: ComponentAuditor | None = None,
        offline_mode: bool = False,
    ) -> None:
        """Inicializa a suíte orquestradora injetando ou instanciando os subsistemas.

        Args:
            researcher: Instância do pesquisador semântico web.
            dom_auditor: Instância do auditor de DOM com suporte a Playwright/fallback.
            visual_engine: Instância do motor de regressão visual diferencial.
            component_auditor: Instância do auditor de micro-componentes de design system.
            offline_mode: Se verdadeiro, prioriza execuções e dados determinísticos offline.
        """
        self.offline_mode = offline_mode
        self.visual_engine = visual_engine or VisualRegressionAuditor()
        self.researcher = researcher or WebResearcher(offline_mode=offline_mode)
        self.dom_auditor = dom_auditor or DOMAuditor()
        self.component_auditor = component_auditor or ComponentAuditor(
            visual_engine=self.visual_engine,
            dom_auditor=self.dom_auditor,
        )

    # =========================================================================
    # Métodos Individuais de Fluxo (Contratos Canônicos)
    # =========================================================================

    def run_semantic_research(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SourceReference]:
        """Executa pesquisa web semântica estruturada e normaliza referências de fontes.

        Args:
            query: Termo de busca.
            limit: Quantidade máxima de artigos/fontes a recuperar.

        Returns:
            Lista de instâncias SourceReference higienizadas.
        """
        return self.researcher.search(query=query, limit=limit)

    def clean_article_html(
        self,
        raw_html: str,
        url: str = "file://local",
        title: str | None = None,
    ) -> SourceReference:
        """Higieniza código HTML ruidoso expurgando scripts, styles, SVG e comentários.

        Args:
            raw_html: Código HTML bruto.
            url: URL canônica associada.
            title: Título opcional de sobreposição.

        Returns:
            SourceReference com texto limpo e metadados.
        """
        return self.researcher.extract_from_html(raw_html=raw_html, url=url, title=title)

    def run_dom_audit(
        self,
        url_or_html: str,
        selectors: list[str] | None = None,
    ) -> list[DOMNodeSummary]:
        """Inspeciona elementos-chave e computa coordenadas geométricas do DOM.

        Args:
            url_or_html: URL web, caminho de arquivo local ou string contendo código HTML.
            selectors: Lista opcional de seletores CSS / tags a inspecionar.

        Returns:
            Lista de instâncias DOMNodeSummary contendo nós e geometrias computadas.
        """
        if _looks_like_raw_html(url_or_html):
            return self.dom_auditor.inspect_html(url_or_html, selectors=selectors)
        return self.dom_auditor.inspect_url(url_or_html, selectors=selectors)

    def run_visual_audit(
        self,
        baseline: str | Path | Any,
        current: str | Path | Any,
        diff_out: str | Path | None = None,
        tolerance: int = 15,
    ) -> VisualDiffResult:
        """Executa auditoria visual diferencial pixel a pixel entre duas imagens.

        Args:
            baseline: Imagem base de referência (PIL.Image, Path ou string).
            current: Imagem atual sob auditoria (PIL.Image, Path ou string).
            diff_out: Caminho opcional para gravação da máscara diferencial (#FF0000).
            tolerance: Limiar de tolerância por canal RGB contra antialiasing (padrão: 15).

        Returns:
            VisualDiffResult com métricas exatas de divergência.
        """
        return self.visual_engine.compare_images(
            baseline_img=baseline,
            current_img=current,
            diff_output_path=diff_out,
            tolerance=tolerance,
        )

    def run_component_audit(
        self,
        baseline: str,
        current: str,
        selectors: list[str],
        diff_dir: str | Path = ".",
    ) -> list[ComponentDiffReport]:
        """Audita micro-componentes isolados por seletores CSS entre duas versões da página.

        Args:
            baseline: URL ou caminho da baseline.
            current: URL ou caminho da versão atual.
            selectors: Lista de seletores CSS delimitando os componentes a inspecionar.
            diff_dir: Diretório onde serão gravados os snapshots e máscaras diferenciais.

        Returns:
            Lista de ComponentDiffReport para cada micro-componente inspecionado.
        """
        return self.component_auditor.audit_components(
            baseline_url=baseline,
            current_url=current,
            selectors=selectors,
            output_dir=diff_dir,
        )

    # =========================================================================
    # Pipeline Integrado Completo (Orquestrador)
    # =========================================================================

    def run_full_suite(
        self,
        config: SuiteConfig | dict[str, Any],
    ) -> SuiteAuditReport:
        """Executa o pipeline consolidado de auditoria completa da aplicação.

        Etapas orquestradas:
        1. Pesquisa semântica opcional (se search_query configurado);
        2. Inspeção estrutural e geométrica do DOM;
        3. Captura e regressão visual diferencial fullpage (máscara diff_result.png);
        4. Isolamento e regressão granular por micro-componentes de design system;
        5. Consolidação de métricas e emissão do SuiteAuditReport.

        Args:
            config: Instância de SuiteConfig ou dicionário com as configurações da suíte.

        Returns:
            SuiteAuditReport contendo todos os achados consolidados e status geral PASS/FAIL.
        """
        cfg = config if isinstance(config, SuiteConfig) else SuiteConfig.model_validate(config)
        out_dir = Path(cfg.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        research_references: list[SourceReference] = []
        dom_nodes: list[DOMNodeSummary] = []
        fullpage_diff: VisualDiffResult | None = None
        component_diffs: list[ComponentDiffReport] = []

        # 1. Pesquisa semântica opcional
        if cfg.search_query:
            try:
                research_references = self.run_semantic_research(
                    query=cfg.search_query,
                    limit=cfg.search_limit,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Falha na pesquisa semântica durante a suíte: %s", exc)

        # 2. Inspeção do DOM
        target_dom_url = cfg.current_url or cfg.baseline_url
        if target_dom_url:
            try:
                dom_nodes = self.run_dom_audit(
                    url_or_html=target_dom_url,
                    selectors=cfg.component_selectors if cfg.component_selectors else None,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Falha na inspeção de DOM durante a suíte: %s", exc)

        # 3. Regressão visual fullpage (tela cheia)
        if cfg.capture_fullpage and cfg.baseline_url and cfg.current_url:
            fullpage_diff = self._execute_fullpage_diff(cfg=cfg, out_dir=out_dir)

        # 4. Auditoria de micro-componentes
        if cfg.component_selectors and cfg.baseline_url and cfg.current_url:
            try:
                component_diffs = self.run_component_audit(
                    baseline=cfg.baseline_url,
                    current=cfg.current_url,
                    selectors=cfg.component_selectors,
                    diff_dir=out_dir,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Falha na auditoria de componentes durante a suíte: %s", exc)

        # 5. Avaliação do status global (PASS / FAIL)
        overall_status = "PASS"

        if fullpage_diff is not None and fullpage_diff.has_divergence:
            overall_status = "FAIL"

        divergent_components = 0
        for comp in component_diffs:
            if comp.status == "diverged" or (
                comp.diff_result is not None and comp.diff_result.has_divergence
            ):
                divergent_components += 1
                overall_status = "FAIL"

        summary_metrics: dict[str, Any] = {
            "overall_status": overall_status,
            "has_divergence": (overall_status == "FAIL"),
            "fullpage_diff_percentage": (
                fullpage_diff.diff_percentage if fullpage_diff else 0.0
            ),
            "fullpage_diff_pixels": (
                fullpage_diff.diff_pixels if fullpage_diff else 0
            ),
            "total_components_audited": len(component_diffs),
            "divergent_components_count": divergent_components,
            "dom_nodes_inspected": len(dom_nodes),
            "research_references_found": len(research_references),
        }

        report = SuiteAuditReport(
            baseline_url=cfg.baseline_url,
            current_url=cfg.current_url,
            research_references=research_references,
            dom_nodes=dom_nodes,
            visual_diff=fullpage_diff,
            component_diffs=component_diffs,
            overall_status=overall_status,
            summary_metrics=summary_metrics,
        )

        # Persistência opcional em JSON
        if cfg.save_report_json:
            report_file = out_dir / "suite_report.json"
            report_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")

        return report

    def _execute_fullpage_diff(
        self,
        cfg: SuiteConfig,
        out_dir: Path,
    ) -> VisualDiffResult | None:
        """Executa a comparação fullpage adaptando se os alvos são imagens ou páginas web."""
        diff_out_path = out_dir / cfg.diff_fullpage_name

        # Cenário A: Ambos os alvos já são arquivos de imagem locais
        if _is_image_path(cfg.baseline_url) and _is_image_path(cfg.current_url):
            try:
                return self.run_visual_audit(
                    baseline=cfg.baseline_url,
                    current=cfg.current_url,
                    diff_out=diff_out_path,
                    tolerance=cfg.tolerance,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Falha ao comparar imagens existentes: %s", exc)
                return None

        # Cenário B: Alvos são páginas web ou HTML; realiza screenshot headless prévio
        try:
            baseline_img_path = out_dir / "baseline_fullpage.png"
            current_img_path = out_dir / "current_fullpage.png"

            self.dom_auditor.capture_fullpage_screenshot(
                url_or_path=cfg.baseline_url,
                output_path=baseline_img_path,
            )
            self.dom_auditor.capture_fullpage_screenshot(
                url_or_path=cfg.current_url,
                output_path=current_img_path,
            )

            return self.run_visual_audit(
                baseline=baseline_img_path,
                current=current_img_path,
                diff_out=diff_out_path,
                tolerance=cfg.tolerance,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falha ao gerar e comparar screenshots fullpage: %s", exc)
            return None
