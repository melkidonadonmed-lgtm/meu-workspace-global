"""Suíte de testes determinísticos para o auditor de micro-componentes.

Valida:
1. Sanitização de seletores CSS para arquivos seguros.
2. Recorte por bounding box (capture_component_from_image).
3. Comparação de snapshots idênticos (status 'matched').
4. Comparação de snapshots divergentes gerando 'diff_<selector_sanitized>.png' com destaque vermelho.
5. Detecção de componente ausente na baseline ('missing_in_baseline') e no current ('missing_in_current').
6. Detecção de alteração dimensional/posicional (geometry_changed = True).
7. Auditoria em lote de múltiplos componentes.
"""

from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from web_visual_auditor.component_auditor import (
    ComponentAuditor,
    sanitize_selector,
)
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


def test_sanitize_selector_produces_safe_filenames() -> None:
    """Verifica que seletores complexos são normalizados para nomes seguros de arquivo."""
    assert sanitize_selector("button.btn-primary") == "button_btn-primary"
    assert sanitize_selector("#main-header > nav ul li") == "main-header_nav_ul_li"
    assert sanitize_selector("article[data-testid='card-1']") == "article_data-testid_card-1"
    assert sanitize_selector("   ") == "component"
    assert sanitize_selector(".card__title--active") == "card__title--active"


def test_capture_component_from_bounding_box(tmp_path: Path) -> None:
    """Valida o recorte cirúrgico de um componente a partir de uma captura maior."""
    # Cria uma imagem 400x300 simulando uma página web
    fullpage = Image.new("RGB", (400, 300), color=(240, 240, 240))
    draw = ImageDraw.Draw(fullpage)
    # Desenha um botão azul na coordenada (50, 100) com tamanho 120x40
    draw.rectangle([50, 100, 169, 139], fill=(37, 99, 235))

    fullpage_file = tmp_path / "fullpage.png"
    fullpage.save(fullpage_file)

    auditor = ComponentAuditor()
    btn_output = tmp_path / "button_snapshot.png"

    snapshot = auditor.capture_component_from_image(
        fullpage_image=fullpage_file,
        selector="button.btn-primary",
        bounding_box=(50, 100, 120, 40),
        output_path=btn_output,
    )

    assert isinstance(snapshot, ComponentSnapshot)
    assert snapshot.selector == "button.btn-primary"
    assert snapshot.dimensions == (120, 40)
    assert snapshot.screenshot_path == str(btn_output)
    assert btn_output.exists()

    with Image.open(btn_output) as img:
        assert img.size == (120, 40)
        # O pixel recortado deve ser o azul do botão (37, 99, 235)
        assert img.getpixel((10, 10)) == (37, 99, 235)


def test_capture_component_invalid_bounding_box(tmp_path: Path) -> None:
    """Verifica disparo de ComponentAuditError ao recortar com dimensões zeradas ou negativas."""
    fullpage = Image.new("RGB", (100, 100), color=(255, 255, 255))
    auditor = ComponentAuditor()

    with pytest.raises(ComponentAuditError) as exc_info:
        auditor.capture_component_from_image(
            fullpage_image=fullpage,
            selector=".broken",
            bounding_box=(0, 0, 0, 50),
            output_path=tmp_path / "out.png",
        )

    assert "Dimensões inválidas" in str(exc_info.value)


def test_compare_component_snapshots_matched(tmp_path: Path) -> None:
    """Verifica que snapshots perfeitamente iguais geram status 'matched'."""
    img_a = Image.new("RGB", (80, 30), color=(0, 128, 0))
    img_b = Image.new("RGB", (80, 30), color=(0, 128, 0))

    snap_a_path = tmp_path / "base_btn.png"
    snap_b_path = tmp_path / "curr_btn.png"
    img_a.save(snap_a_path)
    img_b.save(snap_b_path)

    snap_a = ComponentSnapshot(
        selector="button.confirm",
        dimensions=(80, 30),
        screenshot_path=str(snap_a_path),
        geometry=ComputedElementGeometry(x=10, y=20, width=80, height=30),
    )
    snap_b = ComponentSnapshot(
        selector="button.confirm",
        dimensions=(80, 30),
        screenshot_path=str(snap_b_path),
        geometry=ComputedElementGeometry(x=10, y=20, width=80, height=30),
    )

    auditor = ComponentAuditor()
    report = auditor.compare_component_snapshots(snap_a, snap_b)

    assert isinstance(report, ComponentDiffReport)
    assert report.selector == "button.confirm"
    assert report.status == "matched"
    assert report.geometry_changed is False
    assert report.diff_result is not None
    assert report.diff_result.diff_pixels == 0
    assert report.diff_result.has_divergence is False


def test_compare_component_snapshots_diverged_and_diff_file(tmp_path: Path) -> None:
    """Verifica detecção de divergência e criação de diff_<selector_sanitized>.png."""
    # Baseline: botão verde
    base_img = Image.new("RGB", (100, 40), color=(0, 128, 0))
    # Current: botão que mudou para vermelho
    curr_img = Image.new("RGB", (100, 40), color=(200, 0, 0))

    base_path = tmp_path / "base.png"
    curr_path = tmp_path / "curr.png"
    diff_target = tmp_path / "diff_button_checkout.png"

    base_img.save(base_path)
    curr_img.save(curr_path)

    snap_base = ComponentSnapshot(
        selector="button.checkout",
        dimensions=(100, 40),
        screenshot_path=str(base_path),
    )
    snap_curr = ComponentSnapshot(
        selector="button.checkout",
        dimensions=(100, 40),
        screenshot_path=str(curr_path),
    )

    auditor = ComponentAuditor()
    report = auditor.compare_component_snapshots(
        baseline_snapshot=snap_base,
        current_snapshot=snap_curr,
        diff_output_path=diff_target,
    )

    assert report.status == "diverged"
    assert report.geometry_changed is False
    assert report.diff_result is not None
    assert report.diff_result.has_divergence is True
    assert report.diff_result.diff_pixels == 4000  # Todos os 100x40 pixels divergiram
    assert diff_target.exists()

    with Image.open(diff_target) as d_img:
        # Verifica se o pixel da máscara está marcado com vermelho puro #FF0000
        assert d_img.getpixel((20, 20)) == (255, 0, 0, 255)


def test_compare_component_missing_in_baseline(tmp_path: Path) -> None:
    """Verifica reporte correto quando o componente é novo (ausente na baseline)."""
    curr_img = Image.new("RGB", (50, 50), color=(255, 255, 255))
    curr_path = tmp_path / "new_card.png"
    curr_img.save(curr_path)

    snap_curr = ComponentSnapshot(
        selector=".promo-banner",
        dimensions=(50, 50),
        screenshot_path=str(curr_path),
    )

    auditor = ComponentAuditor()
    report = auditor.compare_component_snapshots(
        baseline_snapshot=None,
        current_snapshot=snap_curr,
        selector=".promo-banner",
    )

    assert report.status == "missing_in_baseline"
    assert report.geometry_changed is True
    assert report.baseline_snapshot is None
    assert report.current_snapshot is not None
    assert report.diff_result is None


def test_compare_component_missing_in_current(tmp_path: Path) -> None:
    """Verifica reporte correto quando o componente foi removido na versão atual."""
    base_img = Image.new("RGB", (50, 50), color=(255, 255, 255))
    base_path = tmp_path / "old_badge.png"
    base_img.save(base_path)

    snap_base = ComponentSnapshot(
        selector=".deprecated-badge",
        dimensions=(50, 50),
        screenshot_path=str(base_path),
    )

    auditor = ComponentAuditor()
    report = auditor.compare_component_snapshots(
        baseline_snapshot=snap_base,
        current_snapshot=None,
        selector=".deprecated-badge",
    )

    assert report.status == "missing_in_current"
    assert report.geometry_changed is True
    assert report.baseline_snapshot is not None
    assert report.current_snapshot is None
    assert report.diff_result is None


def test_compare_component_dimension_changed(tmp_path: Path) -> None:
    """Verifica reporte de divergência quando o componente alterou seu tamanho físico."""
    img_a = Image.new("RGB", (100, 40), color=(255, 255, 255))
    img_b = Image.new("RGB", (120, 40), color=(255, 255, 255))

    path_a = tmp_path / "a.png"
    path_b = tmp_path / "b.png"
    img_a.save(path_a)
    img_b.save(path_b)

    snap_a = ComponentSnapshot(selector="button", dimensions=(100, 40), screenshot_path=str(path_a))
    snap_b = ComponentSnapshot(selector="button", dimensions=(120, 40), screenshot_path=str(path_b))

    auditor = ComponentAuditor()
    report = auditor.compare_component_snapshots(snap_a, snap_b)

    assert report.status == "diverged"
    assert report.geometry_changed is True
    assert report.baseline_dimensions == (100, 40)
    assert report.current_dimensions == (120, 40)


def test_compare_component_position_geometry_changed(tmp_path: Path) -> None:
    """Verifica que mudança de coordenadas computadas (x, y) ativa geometry_changed=True."""
    img = Image.new("RGB", (50, 50), color=(100, 100, 100))
    img_path = tmp_path / "btn.png"
    img.save(img_path)

    snap_a = ComponentSnapshot(
        selector=".floating-btn",
        dimensions=(50, 50),
        screenshot_path=str(img_path),
        geometry=ComputedElementGeometry(x=10, y=20, width=50, height=50),
    )
    # Movido de y=20 para y=80
    snap_b = ComponentSnapshot(
        selector=".floating-btn",
        dimensions=(50, 50),
        screenshot_path=str(img_path),
        geometry=ComputedElementGeometry(x=10, y=80, width=50, height=50),
    )

    auditor = ComponentAuditor()
    report = auditor.compare_component_snapshots(snap_a, snap_b)

    assert report.geometry_changed is True
    assert report.status == "matched"  # Visualmente idêntico, mas geometria alterada


def test_batch_component_audit_workflow(tmp_path: Path) -> None:
    """Valida o fluxo em lote de auditoria de múltiplos componentes isolados."""
    diff_dir = tmp_path / "diffs"
    diff_dir.mkdir(parents=True)

    # Cria snapshots simulados para múltiplos seletores
    selectors = ["header.navbar", "button.primary", "footer.links"]

    # Instância com motor visual injetado
    engine = VisualRegressionAuditor(channel_tolerance=15)
    auditor = ComponentAuditor(visual_engine=engine)

    reports = []
    for sel in selectors:
        safe_sel = sanitize_selector(sel)
        p1 = tmp_path / f"base_{safe_sel}.png"
        p2 = tmp_path / f"curr_{safe_sel}.png"
        diff_file = diff_dir / f"diff_{safe_sel}.png"

        img1 = Image.new("RGB", (60, 30), color=(10, 20, 30))
        # Para button.primary, introduz divergência
        color2 = (200, 20, 30) if "primary" in sel else (10, 20, 30)
        img2 = Image.new("RGB", (60, 30), color=color2)

        img1.save(p1)
        img2.save(p2)

        s1 = ComponentSnapshot(selector=sel, dimensions=(60, 30), screenshot_path=str(p1))
        s2 = ComponentSnapshot(selector=sel, dimensions=(60, 30), screenshot_path=str(p2))

        rep = auditor.compare_component_snapshots(s1, s2, diff_output_path=diff_file)
        reports.append(rep)

    assert len(reports) == 3
    assert reports[0].status == "matched"
    assert reports[1].status == "diverged"
    assert reports[2].status == "matched"

    # Confirma que diff_button_primary.png foi gerado
    expected_diff = diff_dir / "diff_button_primary.png"
    assert expected_diff.exists()


def test_element_not_found_error_properties() -> None:
    """Valida as propriedades e mensagem da exceção ElementNotFoundError."""
    err = ElementNotFoundError(selector=".non-existent-modal")
    assert err.selector == ".non-existent-modal"
    assert ".non-existent-modal" in str(err)
    assert isinstance(err, Exception)

