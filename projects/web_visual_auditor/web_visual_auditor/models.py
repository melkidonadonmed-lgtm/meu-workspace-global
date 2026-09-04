"""Modelos de dados canônicos e estritos para o pacote web_visual_auditor.

Construídos com Pydantic v2 para validação rigorosa, tipagem estrita Python 3.11+,
imutabilidade onde aplicável e suporte nativo à serialização JSON.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SourceReference(BaseModel):
    """Representa uma referência de fonte web recuperada e higienizada."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    title: str = Field(..., description="Título normalizado da página ou artigo")
    url: str = Field(..., description="URL canônica da fonte")
    snippet: str = Field(default="", description="Resumo ou trecho informativo extraído")
    cleaned_text: str = Field(
        default="",
        description="Texto limpo e desprovido de tags scripts, styles ou svgs",
    )
    raw_content: str | None = Field(
        default=None,
        description="Conteúdo bruto original antes da higienização",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados adicionais extraídos da fonte",
    )
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp UTC do momento da extração",
    )


class ComputedElementGeometry(BaseModel):
    """Coordenadas geométricas precisas de um elemento (via getBoundingClientRect)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    x: float = Field(..., description="Coordenada X (left) em pixels")
    y: float = Field(..., description="Coordenada Y (top) em pixels")
    width: float = Field(..., description="Largura renderizada em pixels")
    height: float = Field(..., description="Altura renderizada em pixels")

    @property
    def area(self) -> float:
        """Retorna a área em pixels quadrados do elemento."""
        return max(0.0, self.width) * max(0.0, self.height)

    @property
    def as_tuple(self) -> tuple[float, float, float, float]:
        """Retorna a geometria na tupla (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def intersects(self, other: ComputedElementGeometry) -> bool:
        """Verifica se há sobreposição espacial com outra geometria."""
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.height <= other.y
            or other.y + other.height <= self.y
        )


class DOMNodeSummary(BaseModel):
    """Resumo descritivo e visual de um nó relevante inspecionado no DOM."""

    model_config = ConfigDict(extra="ignore")

    tag_name: str = Field(..., description="Tag HTML do nó em lowercase")
    element_id: str | None = Field(default=None, description="Atributo id do nó")
    classes: list[str] = Field(
        default_factory=list,
        description="Lista de classes CSS associadas",
    )
    text_content: str | None = Field(
        default=None,
        description="Texto limpo e legível contido no elemento",
    )
    is_visible: bool = Field(..., description="Indica se o nó está renderizado e visível")
    geometry: ComputedElementGeometry = Field(
        ...,
        description="Geometria computada no viewport",
    )
    selector: str | None = Field(
        default=None,
        description="Seletor CSS sugerido para localização unívoca",
    )
    attributes: dict[str, str] = Field(
        default_factory=dict,
        description="Atributos chave do elemento",
    )

    @property
    def class_names(self) -> list[str]:
        """Propriedade de conveniência para classes CSS."""
        return self.classes


class VisualDiffResult(BaseModel):
    """Resultado computacional da comparação pixel a pixel entre duas imagens."""

    model_config = ConfigDict(extra="ignore")

    baseline_path: str = Field(..., description="Caminho do arquivo da imagem baseline")
    current_path: str = Field(..., description="Caminho do arquivo da imagem current")
    diff_output_path: str | None = Field(
        default=None,
        description="Caminho da imagem diferencial gerada (máscara de calor)",
    )
    total_pixels: int = Field(..., ge=0, description="Total de pixels avaliados")
    diff_pixels: int = Field(..., ge=0, description="Total de pixels divergentes")
    diff_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentual de divergência (0.0 a 100.0)",
    )
    has_divergence: bool = Field(
        ...,
        description="Verdadeiro se houver pixels com divergência acima da tolerância",
    )
    channel_tolerance: int = Field(
        default=15,
        ge=0,
        le=255,
        description="Limiar de tolerância por canal RGB",
    )
    dimensions_match: bool = Field(
        default=True,
        description="Indica se ambas as imagens possuem a mesma resolução",
    )
    baseline_dimensions: tuple[int, int] | None = Field(
        default=None,
        description="Dimensões (width, height) da imagem baseline",
    )
    current_dimensions: tuple[int, int] | None = Field(
        default=None,
        description="Dimensões (width, height) da imagem current",
    )

    @property
    def diff_image_path(self) -> str | None:
        """Alias para diff_output_path."""
        return self.diff_output_path

    @property
    def total_pixels_count(self) -> int:
        """Alias para total_pixels."""
        return self.total_pixels

    @property
    def diff_pixels_count(self) -> int:
        """Alias para diff_pixels."""
        return self.diff_pixels

    @property
    def has_diff(self) -> bool:
        """Alias de conveniência para has_divergence."""
        return self.has_divergence


class ComponentSnapshot(BaseModel):
    """Captura isolada de um micro-componente delimitado por seletor CSS."""

    model_config = ConfigDict(extra="ignore")

    selector: str = Field(..., description="Seletor CSS que isola o componente")
    dimensions: tuple[int, int] = Field(
        ...,
        description="Dimensões inteiras (width, height) do componente recortado",
    )
    screenshot_path: str = Field(..., description="Caminho da screenshot isolada no disco")
    geometry: ComputedElementGeometry | None = Field(
        default=None,
        description="Geometria computada do componente na página original",
    )
    is_visible: bool = Field(
        default=True,
        description="Indica se o componente estava visível no momento da captura",
    )
    tag_name: str | None = Field(default=None, description="Tag HTML do componente")
    inner_text: str | None = Field(default=None, description="Texto resumido do componente")
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp UTC da captura",
    )


class ComponentDiffReport(BaseModel):
    """Relatório diferencial isolado de um micro-componente de interface."""

    model_config = ConfigDict(extra="ignore")

    selector: str = Field(..., description="Seletor CSS do componente auditado")
    baseline_dimensions: tuple[int, int] | None = Field(
        default=None,
        description="Dimensões (width, height) na baseline",
    )
    current_dimensions: tuple[int, int] | None = Field(
        default=None,
        description="Dimensões (width, height) na versão atual",
    )
    diff_result: VisualDiffResult | None = Field(
        default=None,
        description="Resultado da regressão visual diferencial do componente",
    )
    baseline_snapshot: ComponentSnapshot | None = Field(
        default=None,
        description="Snapshot base capturado",
    )
    current_snapshot: ComponentSnapshot | None = Field(
        default=None,
        description="Snapshot atual capturado",
    )
    status: str = Field(
        default="matched",
        description="Status: matched, diverged, missing_in_baseline, missing_in_current",
    )
    geometry_changed: bool = Field(
        default=False,
        description="Verdadeiro se houve alteração dimensional ou posicional",
    )


class SuiteAuditReport(BaseModel):
    """Relatório consolidado e executivo de auditoria de interface e regressão visual."""

    model_config = ConfigDict(extra="ignore")

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp UTC da execução da suíte",
    )
    baseline_url: str = Field(default="", description="URL ou path da baseline")
    current_url: str = Field(default="", description="URL ou path da versão sob teste")
    research_references: list[SourceReference] = Field(
        default_factory=list,
        description="Fontes e artigos recuperados na pesquisa semântica",
    )
    dom_nodes: list[DOMNodeSummary] = Field(
        default_factory=list,
        description="Elementos-chave inspecionados no DOM",
    )
    visual_diff: VisualDiffResult | None = Field(
        default=None,
        description="Diferencial visual da página completa",
    )
    component_diffs: list[ComponentDiffReport] = Field(
        default_factory=list,
        description="Relatórios diferenciais por micro-componente",
    )
    overall_status: str = Field(
        default="PASS",
        description="Status global: PASS ou FAIL",
    )
    summary_metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Métricas agregadas consolidadas",
    )

    @property
    def execution_timestamp(self) -> datetime:
        """Alias para timestamp."""
        return self.timestamp

    @property
    def fullpage_diff(self) -> VisualDiffResult | None:
        """Alias para visual_diff."""
        return self.visual_diff
