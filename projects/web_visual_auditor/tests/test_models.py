"""Suíte de testes unitários para modelos Pydantic v2 e hierarquia de exceções.

Testa validações rigorosas, imutabilidade, serialização/desserialização JSON
e contratos de herança de exceções em web_visual_auditor.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from web_visual_auditor.exceptions import (
    AuditorError,
    ComponentAuditError,
    ConfigurationError,
    DOMAuditError,
    ElementNotFoundError,
    ImageDimensionMismatchError,
    ImageLoadError,
    NavigationTimeoutError,
    PageNavigationTimeoutError,
    ResearchError,
    SemanticExtractionError,
    VisualRegressionError,
    WebVisualAuditorError,
)
from web_visual_auditor.models import (
    ComponentDiffReport,
    ComponentSnapshot,
    ComputedElementGeometry,
    DOMNodeSummary,
    SourceReference,
    SuiteAuditReport,
    VisualDiffResult,
)

# ==============================================================================
# 1. Testes da Hierarquia de Exceções
# ==============================================================================


def test_exception_hierarchy_base_auditor_error() -> None:
    """Garante que todas as exceções especializadas herdam de AuditorError."""
    exceptions_to_check = [
        WebVisualAuditorError,
        ResearchError,
        SemanticExtractionError,
        DOMAuditError,
        NavigationTimeoutError,
        PageNavigationTimeoutError,
        ElementNotFoundError,
        VisualRegressionError,
        ImageDimensionMismatchError,
        ImageLoadError,
        ComponentAuditError,
        ConfigurationError,
    ]
    for exc_cls in exceptions_to_check:
        assert issubclass(exc_cls, AuditorError), f"{exc_cls.__name__} deve herdar de AuditorError"


def test_dom_exception_inheritance() -> None:
    """Garante a cadeia de herança das exceções de DOM."""
    assert issubclass(NavigationTimeoutError, DOMAuditError)
    assert issubclass(PageNavigationTimeoutError, NavigationTimeoutError)
    assert issubclass(ElementNotFoundError, DOMAuditError)


def test_element_not_found_error_payload() -> None:
    """Verifica mensagem e atributos capturados em ElementNotFoundError."""
    err = ElementNotFoundError("button.submit-btn")
    assert err.selector == "button.submit-btn"
    assert "button.submit-btn" in str(err)
    assert isinstance(err, DOMAuditError)
    assert isinstance(err, AuditorError)


def test_image_dimension_mismatch_error_payload() -> None:
    """Verifica atributos dimensionais em ImageDimensionMismatchError."""
    err = ImageDimensionMismatchError((1920, 1080), (1280, 720))
    assert err.baseline_dims == (1920, 1080)
    assert err.current_dims == (1280, 720)
    assert "1920, 1080" in str(err)
    assert isinstance(err, VisualRegressionError)
    assert isinstance(err, AuditorError)


def test_auditor_catch_all() -> None:
    """Testa captura polimórfica usando AuditorError genérico."""
    with pytest.raises(AuditorError) as exc_info:
        raise SemanticExtractionError("Falha ao analisar árvore sintática de nós")
    assert isinstance(exc_info.value, ResearchError)
    assert "Falha ao analisar" in str(exc_info.value)


# ==============================================================================
# 2. Testes de SourceReference
# ==============================================================================


def test_source_reference_creation_and_defaults() -> None:
    """Valida instanciação de SourceReference e valores padrão."""
    ref = SourceReference(
        title="Guia de Design Systems",
        url="https://example.com/design-system",
    )
    assert ref.title == "Guia de Design Systems"
    assert ref.url == "https://example.com/design-system"
    assert ref.snippet == ""
    assert ref.cleaned_text == ""
    assert ref.raw_content is None
    assert ref.metadata == {}
    assert isinstance(ref.extracted_at, datetime)


def test_source_reference_immutability() -> None:
    """Garante que SourceReference é congelado (frozen=True)."""
    ref = SourceReference(
        title="Página Original",
        url="https://test.com",
    )
    with pytest.raises(ValidationError):
        # Tentativa de mutação direta deve ser rejeitada pelo Pydantic
        ref.title = "Novo Título"  # type: ignore[misc]


def test_source_reference_forbids_extra_fields() -> None:
    """Garante rejeição estrita de campos não mapeados."""
    with pytest.raises(ValidationError):
        SourceReference(
            title="Página Teste",
            url="https://test.com",
            campo_desconhecido="valor_invalido",  # type: ignore[call-arg]
        )


def test_source_reference_json_roundtrip() -> None:
    """Testa serialização para JSON e restauração completa."""
    ref = SourceReference(
        title="Artigo Completo",
        url="https://design.gov.br/tokens",
        snippet="Introdução aos tokens de espaçamento e tipografia...",
        cleaned_text="Introdução aos tokens.",
        metadata={"author": "Designer Chefe", "views": 1250},
    )
    json_data = ref.model_dump_json()
    restored = SourceReference.model_validate_json(json_data)
    assert restored.title == ref.title
    assert restored.url == ref.url
    assert restored.metadata["views"] == 1250


# ==============================================================================
# 3. Testes de ComputedElementGeometry
# ==============================================================================


def test_computed_element_geometry_attributes_and_area() -> None:
    """Testa cálculo de área e conversão de tupla."""
    geo = ComputedElementGeometry(x=10.0, y=20.0, width=100.0, height=50.0)
    assert geo.x == 10.0
    assert geo.y == 20.0
    assert geo.width == 100.0
    assert geo.height == 50.0
    assert geo.area == 5000.0
    assert geo.as_tuple == (10.0, 20.0, 100.0, 50.0)


def test_computed_element_geometry_intersection() -> None:
    """Testa detecção espacial de colisão/interseção."""
    g1 = ComputedElementGeometry(x=0.0, y=0.0, width=50.0, height=50.0)
    g2 = ComputedElementGeometry(x=25.0, y=25.0, width=50.0, height=50.0)
    g3 = ComputedElementGeometry(x=100.0, y=100.0, width=20.0, height=20.0)

    # g1 e g2 se sobrepõem
    assert g1.intersects(g2) is True
    assert g2.intersects(g1) is True

    # g1 e g3 estão completamente separados
    assert g1.intersects(g3) is False
    assert g3.intersects(g1) is False

    # Apenas tocando a borda (x=50.0) não deve ser considerado interseção
    g_edge = ComputedElementGeometry(x=50.0, y=0.0, width=20.0, height=50.0)
    assert g1.intersects(g_edge) is False


def test_computed_element_geometry_immutability() -> None:
    """Garante imutabilidade de coordenadas."""
    geo = ComputedElementGeometry(x=10.0, y=20.0, width=30.0, height=40.0)
    with pytest.raises(ValidationError):
        geo.x = 99.0  # type: ignore[misc]


# ==============================================================================
# 4. Testes de DOMNodeSummary
# ==============================================================================


def test_dom_node_summary_creation() -> None:
    """Testa modelo DOMNodeSummary e geometria aninhada."""
    geo = ComputedElementGeometry(x=0.0, y=0.0, width=320.0, height=48.0)
    node = DOMNodeSummary(
        tag_name="header",
        element_id="main-header",
        classes=["site-header", "fixed-top"],
        text_content="Portal de Serviços",
        is_visible=True,
        geometry=geo,
        selector="header#main-header",
        attributes={"role": "banner"},
    )
    assert node.tag_name == "header"
    assert node.element_id == "main-header"
    assert node.classes == ["site-header", "fixed-top"]
    assert node.class_names == ["site-header", "fixed-top"]
    assert node.is_visible is True
    assert node.geometry.width == 320.0
    assert node.attributes["role"] == "banner"


def test_dom_node_summary_json_roundtrip() -> None:
    """Valida ciclo completo JSON em nós de DOM."""
    geo = ComputedElementGeometry(x=50.0, y=100.0, width=120.0, height=36.0)
    node = DOMNodeSummary(
        tag_name="button",
        element_id="cta-buy",
        classes=["btn", "btn-primary"],
        is_visible=True,
        geometry=geo,
    )
    serialized = node.model_dump_json()
    data = json.loads(serialized)
    assert data["tag_name"] == "button"
    assert data["geometry"]["x"] == 50.0

    restored = DOMNodeSummary.model_validate_json(serialized)
    assert restored.geometry.area == 120.0 * 36.0


# ==============================================================================
# 5. Testes de VisualDiffResult
# ==============================================================================


def test_visual_diff_result_valid_metrics() -> None:
    """Testa cálculo e propriedades de divergência visual."""
    diff = VisualDiffResult(
        baseline_path="baseline.png",
        current_path="current.png",
        diff_output_path="diff.png",
        total_pixels=10000,
        diff_pixels=250,
        diff_percentage=2.5,
        has_divergence=True,
        channel_tolerance=15,
        baseline_dimensions=(100, 100),
        current_dimensions=(100, 100),
    )
    assert diff.diff_percentage == 2.5
    assert diff.has_divergence is True
    assert diff.diff_pixels == 250
    assert diff.total_pixels == 10000
    assert diff.diff_image_path == "diff.png"
    assert diff.total_pixels_count == 10000
    assert diff.diff_pixels_count == 250


def test_visual_diff_result_validation_limits() -> None:
    """Verifica restrições de limite para percentual e contagem de pixels."""
    # diff_percentage acima de 100.0 deve falhar
    with pytest.raises(ValidationError):
        VisualDiffResult(
            baseline_path="a.png",
            current_path="b.png",
            total_pixels=100,
            diff_pixels=105,
            diff_percentage=105.0,
            has_divergence=True,
        )

    # diff_percentage negativo deve falhar
    with pytest.raises(ValidationError):
        VisualDiffResult(
            baseline_path="a.png",
            current_path="b.png",
            total_pixels=100,
            diff_pixels=0,
            diff_percentage=-0.5,
            has_divergence=False,
        )


# ==============================================================================
# 6. Testes de ComponentSnapshot e ComponentDiffReport
# ==============================================================================


def test_component_snapshot_and_diff_report() -> None:
    """Testa snapshots de componentes e relatórios de diff associados."""
    geo_base = ComputedElementGeometry(x=10.0, y=10.0, width=150.0, height=40.0)
    snap_base = ComponentSnapshot(
        selector="button.primary",
        dimensions=(150, 40),
        screenshot_path="button_base.png",
        geometry=geo_base,
        is_visible=True,
        tag_name="button",
        inner_text="Confirmar",
    )

    snap_curr = ComponentSnapshot(
        selector="button.primary",
        dimensions=(150, 40),
        screenshot_path="button_curr.png",
        geometry=geo_base,
        is_visible=True,
        tag_name="button",
        inner_text="Confirmar",
    )

    diff_res = VisualDiffResult(
        baseline_path="button_base.png",
        current_path="button_curr.png",
        diff_output_path=None,
        total_pixels=6000,
        diff_pixels=0,
        diff_percentage=0.0,
        has_divergence=False,
        baseline_dimensions=(150, 40),
        current_dimensions=(150, 40),
    )

    report = ComponentDiffReport(
        selector="button.primary",
        baseline_dimensions=(150, 40),
        current_dimensions=(150, 40),
        diff_result=diff_res,
        baseline_snapshot=snap_base,
        current_snapshot=snap_curr,
        status="matched",
        geometry_changed=False,
    )

    assert report.status == "matched"
    assert report.diff_result is not None
    assert report.diff_result.has_divergence is False
    assert report.geometry_changed is False

    # Serialização do relatório de componente
    dumped = report.model_dump()
    assert dumped["selector"] == "button.primary"
    assert tuple(dumped["baseline_dimensions"]) == (150, 40)

# ==============================================================================
# 7. Testes de SuiteAuditReport
# ==============================================================================


def test_suite_audit_report_consolidation() -> None:
    """Testa o modelo agregador SuiteAuditReport com múltiplos nós e diffs."""
    now_utc = datetime.now(UTC)
    geo = ComputedElementGeometry(x=0.0, y=0.0, width=800.0, height=60.0)
    header_node = DOMNodeSummary(
        tag_name="nav",
        is_visible=True,
        geometry=geo,
        selector="nav.navbar",
    )

    source = SourceReference(
        title="Documentação Oficial",
        url="https://docs.local",
        snippet="Guia de auditoria",
    )

    full_diff = VisualDiffResult(
        baseline_path="page_v1.png",
        current_path="page_v2.png",
        diff_output_path="page_diff.png",
        total_pixels=800000,
        diff_pixels=1200,
        diff_percentage=0.15,
        has_divergence=True,
    )

    comp_report = ComponentDiffReport(
        selector="nav.navbar",
        baseline_dimensions=(800, 60),
        current_dimensions=(800, 60),
        diff_result=full_diff,
        status="diverged",
    )

    suite_report = SuiteAuditReport(
        timestamp=now_utc,
        baseline_url="file:///app/v1.html",
        current_url="file:///app/v2.html",
        research_references=[source],
        dom_nodes=[header_node],
        visual_diff=full_diff,
        component_diffs=[comp_report],
        overall_status="FAIL",
        summary_metrics={"total_components": 1, "diverged_components": 1},
    )

    assert suite_report.overall_status == "FAIL"
    assert len(suite_report.dom_nodes) == 1
    assert len(suite_report.research_references) == 1
    assert len(suite_report.component_diffs) == 1
    assert suite_report.fullpage_diff == full_diff
    assert suite_report.execution_timestamp == now_utc

    # Roundtrip JSON
    json_str = suite_report.model_dump_json()
    restored = SuiteAuditReport.model_validate_json(json_str)
    assert restored.baseline_url == "file:///app/v1.html"
    assert restored.dom_nodes[0].tag_name == "nav"
    assert restored.visual_diff is not None
    assert restored.visual_diff.diff_pixels == 1200
