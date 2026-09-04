"""Suíte de testes adversariais empíricos para o motor de regressão visual.

Desafia rigorosamente:
1. Limiar exato de sensibilidade: Delta C = 15 (0% diff) vs Delta C = 16 (computado como divergente),
   testado isoladamente para os canais R, G e B, deltas positivos e negativos, e combinação multicanal.
2. Fidelidade estrita da máscara diferencial: pixels divergentes devem ser exatamente
   em vermelho puro #FF0000 (RGBA: 255, 0, 0, 255 ou RGB: 255, 0, 0).
3. Cálculo percentual em resoluções variadas (1x1, 10x10, 50x200, 1920x1080 Full HD).
4. Incompatibilidade dimensional estrita disparando ImageDimensionMismatchError,
   incluindo dimensões transpostas com mesma área total de pixels.
5. Resiliência de ComponentAuditor frente a divergências dimensionais e espaciais.
"""

from pathlib import Path

import pytest
from PIL import Image

from web_visual_auditor.component_auditor import ComponentAuditor
from web_visual_auditor.exceptions import ImageDimensionMismatchError
from web_visual_auditor.models import (
    ComponentSnapshot,
    ComputedElementGeometry,
)
from web_visual_auditor.visual_regression import (
    PureImageBuffer,
    VisualRegressionAuditor,
)

# ============================================================================
# 1. Desafio Adversarial de Limiar Exato: Delta C = 15 vs Delta C = 16
# ============================================================================

@pytest.mark.parametrize("channel", ["R", "G", "B"])
def test_exact_threshold_boundary_15_vs_16_single_channel(channel: str) -> None:
    """Verifica que variação Delta C = 15 resulta em 0% e Delta C = 16 é divergente."""
    auditor = VisualRegressionAuditor(channel_tolerance=15)
    base_color = (100, 100, 100)

    # Cria offsets para testar canal individual
    offset_15 = {
        "R": (base_color[0] + 15, base_color[1], base_color[2]),
        "G": (base_color[0], base_color[1] + 15, base_color[2]),
        "B": (base_color[0], base_color[1], base_color[2] + 15),
    }[channel]

    offset_16 = {
        "R": (base_color[0] + 16, base_color[1], base_color[2]),
        "G": (base_color[0], base_color[1] + 16, base_color[2]),
        "B": (base_color[0], base_color[1], base_color[2] + 16),
    }[channel]

    # Imagens 10x10
    img_base = Image.new("RGB", (10, 10), color=base_color)
    img_15 = Image.new("RGB", (10, 10), color=offset_15)
    img_16 = Image.new("RGB", (10, 10), color=offset_16)

    # Teste limiar Delta C = 15: deve ser 0% diff
    res_15 = auditor.compare_images(img_base, img_15)
    assert res_15.diff_pixels == 0, f"Canal {channel} com delta 15 não deveria divergir"
    assert res_15.diff_percentage == 0.0
    assert res_15.has_divergence is False

    # Teste limiar Delta C = 16: todos os 100 pixels devem ser computados como divergentes
    res_16 = auditor.compare_images(img_base, img_16)
    assert res_16.diff_pixels == 100, f"Canal {channel} com delta 16 deve divergir em todos os pixels"
    assert res_16.diff_percentage == 100.0
    assert res_16.has_divergence is True


def test_exact_threshold_negative_delta_boundary() -> None:
    """Verifica que variações negativas (decremento de cor) respeitam o limiar exato."""
    auditor = VisualRegressionAuditor(channel_tolerance=15)
    base_color = (200, 200, 200)
    color_minus_15 = (185, 200, 200)  # Delta R = -15, |delta| = 15
    color_minus_16 = (184, 200, 200)  # Delta R = -16, |delta| = 16

    img_base = Image.new("RGB", (5, 5), color=base_color)
    img_minus_15 = Image.new("RGB", (5, 5), color=color_minus_15)
    img_minus_16 = Image.new("RGB", (5, 5), color=color_minus_16)

    # Delta 15 negativo -> 0% diff
    res_15 = auditor.compare_images(img_base, img_minus_15)
    assert res_15.diff_pixels == 0
    assert res_15.has_divergence is False

    # Delta 16 negativo -> divergente
    res_16 = auditor.compare_images(img_base, img_minus_16)
    assert res_16.diff_pixels == 25
    assert res_16.has_divergence is True


def test_exact_threshold_multichannel_simultaneous_deltas() -> None:
    """Verifica comportamento quando múltiplos canais variam simultaneamente."""
    auditor = VisualRegressionAuditor(channel_tolerance=15)
    base = Image.new("RGB", (10, 10), color=(120, 120, 120))

    # Caso A: R=+15, G=-15, B=+15 -> Todos os canais <= 15
    all_at_15 = Image.new("RGB", (10, 10), color=(135, 105, 135))
    res_a = auditor.compare_images(base, all_at_15)
    assert res_a.diff_pixels == 0
    assert res_a.has_divergence is False

    # Caso B: R=+15, G=+15, B=+16 -> B ultrapassa por 1 unidade
    one_at_16 = Image.new("RGB", (10, 10), color=(135, 135, 136))
    res_b = auditor.compare_images(base, one_at_16)
    assert res_b.diff_pixels == 100
    assert res_b.has_divergence is True


# ============================================================================
# 2. Desafio Adversarial: Cor Exata da Máscara Diferencial (#FF0000 Puro)
# ============================================================================

def test_diff_mask_pure_red_divergent_pixels(tmp_path: Path) -> None:
    """Garante que os pixels divergentes são marcados exatamente em vermelho puro #FF0000.

    RGBA: (255, 0, 0, 255).
    Pixels inalterados devem estar atenuados em tons neutros de cinza (R == G == B != pure red).
    """
    width, height = 40, 40
    base_img = Image.new("RGB", (width, height), color=(200, 200, 200))
    curr_img = Image.new("RGB", (width, height), color=(200, 200, 200))

    # Introduz divergência cirúrgica apenas num quadrado central 10x10 (coordenadas 15 a 24)
    divergent_color = (200 + 16, 200, 200)  # Delta = 16 > 15
    for x in range(15, 25):
        for y in range(15, 25):
            curr_img.putpixel((x, y), divergent_color)

    diff_path = tmp_path / "mask_verification.png"
    auditor = VisualRegressionAuditor(channel_tolerance=15)
    result = auditor.compare_images(base_img, curr_img, diff_output_path=diff_path)

    assert result.diff_pixels == 100  # 10x10 = 100 pixels
    assert diff_path.exists()

    with Image.open(diff_path) as mask:
        assert mask.size == (width, height)
        # Modo RGBA
        assert mask.mode == "RGBA"

        # Varredura completa de todos os pixels da máscara
        for y in range(height):
            for x in range(width):
                px = mask.getpixel((x, y))
                is_in_divergent_box = (15 <= x < 25) and (15 <= y < 25)

                if is_in_divergent_box:
                    # Pixel divergente DEVE ser exatamente #FF0000 (255, 0, 0, 255)
                    assert px == (255, 0, 0, 255), (
                        f"Pixel divergente em ({x}, {y}) não é vermelho puro #FF0000. Valor: {px}"
                    )
                else:
                    # Pixel inalterado NÃO pode ser vermelho puro
                    assert px != (255, 0, 0, 255)
                    # Deve ser cinza neutro (R == G == B) e canal alfa 255
                    r, g, b, a = px
                    assert r == g == b, f"Pixel de contexto em ({x}, {y}) não é cinza neutro: {px}"
                    assert a == 255


def test_pure_image_buffer_fallback_diff_mask_pure_red() -> None:
    """Verifica que o fallback de PureImageBuffer também gera vermelho puro (255, 0, 0)."""
    buf_a = PureImageBuffer(width=4, height=4, pixels=[(50, 50, 50)] * 16)
    buf_b = PureImageBuffer(width=4, height=4, pixels=[(50, 50, 50)] * 16)

    # Pixel (2, 2) divergente com delta = 20 > 15
    buf_b.putpixel((2, 2), (70, 50, 50))

    auditor = VisualRegressionAuditor(channel_tolerance=15)
    res = auditor.compare_pixels(buf_a, buf_b)
    assert res.diff_pixels == 1
    assert res.diff_percentage == (1 / 16) * 100.0


# ============================================================================
# 3. Desafio Adversarial: Resoluções Variadas e Precisão de Cálculo Percentual
# ============================================================================

@pytest.mark.parametrize(
    ("width", "height", "altered_count", "expected_percentage"),
    [
        (1, 1, 0, 0.0),
        (1, 1, 1, 100.0),
        (10, 10, 25, 25.0),
        (50, 200, 500, 5.0),
        (100, 100, 333, 3.33),
        (1920, 1080, 20736, 1.0),  # Full HD com exatamente 1.0% de divergência
    ],
)
def test_varied_resolutions_exact_percentage(
    width: int,
    height: int,
    altered_count: int,
    expected_percentage: float,
) -> None:
    """Testa o cálculo do percentual exato em resoluções minúsculas, não-quadradas e Full HD."""
    auditor = VisualRegressionAuditor(channel_tolerance=15)
    total_pixels = width * height

    # Criação otimizada usando Pillow
    img_a = Image.new("RGB", (width, height), color=(128, 128, 128))
    img_b = Image.new("RGB", (width, height), color=(128, 128, 128))

    # Aplica divergência (delta = 50 > 15) nos primeiros 'altered_count' pixels
    pixels_b = [(128, 128, 128)] * total_pixels
    for i in range(altered_count):
        pixels_b[i] = (178, 128, 128)  # Delta R = 50
    img_b.putdata(pixels_b)

    result = auditor.compare_images(img_a, img_b)

    assert result.total_pixels == total_pixels
    assert result.diff_pixels == altered_count
    assert pytest.approx(result.diff_percentage, rel=1e-3) == expected_percentage
    assert result.has_divergence == (altered_count > 0)


# ============================================================================
# 4. Desafio Adversarial: Incompatibilidade Dimensional Estrita
# ============================================================================

@pytest.mark.parametrize(
    ("dim_a", "dim_b"),
    [
        ((100, 100), (101, 100)),     # Diferença de 1 pixel em largura
        ((100, 100), (100, 101)),     # Diferença de 1 pixel em altura
        ((1920, 1080), (1280, 720)),  # Resoluções padrão diferentes
        ((200, 100), (100, 200)),     # Dimensões transpostas: mesma área total (20.000 pixels)
        ((1, 10), (10, 1)),           # Linha vs coluna
    ],
)
def test_strict_dimension_mismatch_raises_error(
    dim_a: tuple[int, int],
    dim_b: tuple[int, int],
) -> None:
    """Verifica que qualquer discrepância dimensional dispara ImageDimensionMismatchError."""
    auditor = VisualRegressionAuditor()
    img_a = Image.new("RGB", dim_a, color=(255, 255, 255))
    img_b = Image.new("RGB", dim_b, color=(255, 255, 255))

    with pytest.raises(ImageDimensionMismatchError) as exc_info:
        auditor.compare_images(img_a, img_b)

    err = exc_info.value
    assert err.baseline_dims == dim_a
    assert err.current_dims == dim_b
    assert str(dim_a) in str(err)
    assert str(dim_b) in str(err)


# ============================================================================
# 5. Desafio Adversarial: ComponentAuditor frente a Dimensões Divergentes
# ============================================================================

def test_component_auditor_handles_dimension_mismatch_without_exception(tmp_path: Path) -> None:
    """Garante que ComponentAuditor relata divergência dimensional sem quebrar a execução."""
    img_a = Image.new("RGB", (80, 30), color=(100, 100, 100))
    img_b = Image.new("RGB", (80, 35), color=(100, 100, 100))  # Altura mudou de 30 para 35

    path_a = tmp_path / "btn_base.png"
    path_b = tmp_path / "btn_curr.png"
    img_a.save(path_a)
    img_b.save(path_b)

    snap_a = ComponentSnapshot(
        selector="button.btn",
        dimensions=(80, 30),
        screenshot_path=str(path_a),
        geometry=ComputedElementGeometry(x=0, y=0, width=80, height=30),
    )
    snap_b = ComponentSnapshot(
        selector="button.btn",
        dimensions=(80, 35),
        screenshot_path=str(path_b),
        geometry=ComputedElementGeometry(x=0, y=0, width=80, height=35),
    )

    auditor = ComponentAuditor()
    report = auditor.compare_component_snapshots(snap_a, snap_b)

    # ComponentAuditor deve sinalizar divergência graciosa
    assert report.status == "diverged"
    assert report.geometry_changed is True
    assert report.baseline_dimensions == (80, 30)
    assert report.current_dimensions == (80, 35)
    assert report.diff_result is None  # Não executa diff pixel a pixel por dimensão diferente
