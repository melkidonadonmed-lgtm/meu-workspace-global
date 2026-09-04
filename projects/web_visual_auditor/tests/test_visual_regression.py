"""Suíte de testes determinísticos para o motor de regressão visual pixel a pixel.

Valida:
1. Imagens idênticas com 0% de divergência e 0 pixels alterados.
2. Antialiasing e ruídos suaves (delta <= 15) não computados como divergência.
3. Divergência controlada de quadrado 20x20 sobre 100x100 (exatamente 400 pixels = 4.00%).
4. Geração física da máscara diferencial com pixels em vermelho puro #FF0000.
5. Incompatibilidade de dimensões disparando ImageDimensionMismatchError.
6. Ajuste dinâmico de tolerância e tratamento de erros de leitura de arquivo.
"""

from pathlib import Path

import pytest
from PIL import Image

from tests.fixtures.image_fixtures import (
    generate_dimension_mismatch_pair,
    generate_divergent_square_pair,
    generate_identical_pair,
    generate_subtle_noise_pair,
    save_image_pair_to_disk,
)
from web_visual_auditor.exceptions import (
    ImageDimensionMismatchError,
    ImageLoadError,
    VisualRegressionError,
)
from web_visual_auditor.models import VisualDiffResult
from web_visual_auditor.visual_regression import (
    PureImageBuffer,
    VisualRegressionAuditor,
    VisualRegressionEngine,
)


def test_identical_images_zero_divergence() -> None:
    """Verifica que imagens idênticas retornam 0.0% de divergência e 0 pixels alterados."""
    baseline, current = generate_identical_pair(width=100, height=100)
    auditor = VisualRegressionAuditor(channel_tolerance=15)

    result = auditor.compare_images(baseline, current)

    assert isinstance(result, VisualDiffResult)
    assert result.total_pixels == 10000
    assert result.diff_pixels == 0
    assert result.diff_percentage == 0.0
    assert result.has_divergence is False
    assert result.dimensions_match is True
    assert result.baseline_dimensions == (100, 100)
    assert result.current_dimensions == (100, 100)


def test_subtle_noise_antialiasing_tolerance() -> None:
    """Verifica que variações de canal delta <= 15 são absorvidas pela tolerância (0% diff)."""
    # Ruído de 10 unidades por canal (255 -> 245)
    baseline, current = generate_subtle_noise_pair(
        width=100,
        height=100,
        base_color=(255, 255, 255),
        noise_delta=10,
    )
    auditor = VisualRegressionAuditor(channel_tolerance=15)

    result = auditor.compare_images(baseline, current)

    assert result.diff_pixels == 0
    assert result.diff_percentage == 0.0
    assert result.has_divergence is False

    # Ruído exatamente no limite superior (delta = 15)
    baseline_limit, current_limit = generate_subtle_noise_pair(
        width=80,
        height=80,
        base_color=(200, 200, 200),
        noise_delta=15,
    )
    res_limit = auditor.compare_images(baseline_limit, current_limit)
    assert res_limit.diff_pixels == 0
    assert res_limit.diff_percentage == 0.0
    assert res_limit.has_divergence is False


def test_controlled_divergent_square_and_diff_mask(tmp_path: Path) -> None:
    """Valida divergência controlada: quadrado 20x20 sobre 100x100 (400 pixels = 4.00%).

    Comprova também a geração do arquivo diff_result.png e que o pixel divergente
    possui a cor vermelha pura #FF0000 (255, 0, 0, 255) na máscara.
    """
    baseline, current = generate_divergent_square_pair(
        width=100,
        height=100,
        base_color=(255, 255, 255),
        square_color=(0, 0, 0),  # Delta = 255 > 15
        square_size=20,
        top_left=(40, 40),
    )

    diff_file = tmp_path / "diff_result.png"
    auditor = VisualRegressionAuditor(channel_tolerance=15)

    result = auditor.compare_images(
        baseline_img=baseline,
        current_img=current,
        diff_output_path=diff_file,
    )

    # Verificações matemáticas estritas
    assert result.total_pixels == 10000
    assert result.diff_pixels == 400
    assert pytest.approx(result.diff_percentage, rel=1e-5) == 4.00
    assert result.has_divergence is True
    assert result.diff_output_path == str(diff_file)

    # Comprovação da existência do arquivo físico
    assert diff_file.exists()
    assert diff_file.stat().st_size > 0

    # Comprovação de inspeção de pixels na máscara gerada
    with Image.open(diff_file) as diff_img:
        assert diff_img.size == (100, 100)

        # Pixel dentro da região alterada (40 <= x < 60, 40 <= y < 60)
        altered_pixel = diff_img.getpixel((50, 50))
        # Deve ser vermelho puro #FF0000 (RGBA: 255, 0, 0, 255)
        assert altered_pixel == (255, 0, 0, 255), f"Esperado vermelho puro, recebido: {altered_pixel}"

        # Pixel fora da região alterada (fundo inalterado)
        unaltered_pixel = diff_img.getpixel((10, 10))
        # Não pode ser vermelho puro
        assert altered_pixel != unaltered_pixel
        # Deve ser o tom de fundo atenuado
        assert unaltered_pixel[0] == unaltered_pixel[1] == unaltered_pixel[2]


def test_dimension_mismatch_raises_error() -> None:
    """Verifica que imagens de tamanhos diferentes disparam ImageDimensionMismatchError."""
    img_a, img_b = generate_dimension_mismatch_pair(
        dim_a=(100, 100),
        dim_b=(120, 100),
    )
    auditor = VisualRegressionAuditor()

    with pytest.raises(ImageDimensionMismatchError) as exc_info:
        auditor.compare_images(img_a, img_b)

    err = exc_info.value
    assert err.baseline_dims == (100, 100)
    assert err.current_dims == (120, 100)
    assert "100, 100" in str(err)
    assert "120, 100" in str(err)


def test_file_inputs_from_disk(tmp_path: Path) -> None:
    """Valida leitura direta a partir de caminhos de arquivos PNG no disco."""
    baseline, current = generate_identical_pair(width=64, height=64)
    base_file, curr_file = save_image_pair_to_disk(
        baseline=baseline,
        current=current,
        output_dir=tmp_path,
        baseline_filename="base_btn.png",
        current_filename="curr_btn.png",
    )

    auditor = VisualRegressionAuditor()
    result = auditor.compare_images(str(base_file), str(curr_file))

    assert result.diff_pixels == 0
    assert result.has_divergence is False
    assert result.baseline_path == str(base_file)
    assert result.current_path == str(curr_file)


def test_file_not_found_raises_image_load_error(tmp_path: Path) -> None:
    """Verifica lançamento de ImageLoadError para arquivos inexistentes."""
    auditor = VisualRegressionAuditor()
    non_existent = tmp_path / "does_not_exist.png"

    with pytest.raises(ImageLoadError) as exc_info:
        auditor.compare_images(str(non_existent), str(non_existent))

    assert "Arquivo de imagem não encontrado" in str(exc_info.value)


def test_custom_tolerance_override() -> None:
    """Verifica a sobrescrita dinâmica de tolerância no método compare_images."""
    # Ruído de 10 unidades: aceito com tol=15, mas divergente com tol=5
    baseline, current = generate_subtle_noise_pair(
        width=50,
        height=50,
        base_color=(200, 200, 200),
        noise_delta=10,
    )
    auditor = VisualRegressionAuditor(channel_tolerance=15)

    # Com tolerância da instância (15): sem divergência
    res_default = auditor.compare_images(baseline, current)
    assert res_default.diff_pixels == 0

    # Sobrescrevendo para tolerância 5: todas as 2500 posições divergem
    res_strict = auditor.compare_images(baseline, current, tolerance=5)
    assert res_strict.diff_pixels == 2500
    assert res_strict.diff_percentage == 100.0
    assert res_strict.has_divergence is True


def test_invalid_tolerance_bounds() -> None:
    """Verifica que tolerâncias menores que 0 ou maiores que 255 disparam exceção."""
    with pytest.raises(VisualRegressionError):
        VisualRegressionAuditor(channel_tolerance=-1)

    with pytest.raises(VisualRegressionError):
        VisualRegressionAuditor(channel_tolerance=256)

    auditor = VisualRegressionAuditor()
    b, c = generate_identical_pair(10, 10)
    with pytest.raises(VisualRegressionError):
        auditor.compare_images(b, c, tolerance=-5)


def test_canonical_engine_alias() -> None:
    """Garante que VisualRegressionEngine é um alias compatível com VisualRegressionAuditor."""
    assert VisualRegressionEngine is VisualRegressionAuditor
    engine = VisualRegressionEngine()
    assert isinstance(engine, VisualRegressionAuditor)


def test_pure_image_buffer_fallback(tmp_path: Path) -> None:
    """Valida o funcionamento do buffer de imagem puro para cenários sem Pillow."""
    buf_a = PureImageBuffer(width=10, height=10, pixels=[(255, 255, 255)] * 100)
    buf_b = PureImageBuffer(width=10, height=10, pixels=[(255, 255, 255)] * 100)

    # Altera um pixel no centro (5, 5)
    buf_b.putpixel((5, 5), (0, 0, 0))

    auditor = VisualRegressionAuditor(channel_tolerance=15)
    diff_ppm = tmp_path / "diff_pure.ppm"

    res = auditor.compare_pixels(
        img_baseline=buf_a,
        img_current=buf_b,
        diff_output_path=diff_ppm,
    )

    assert res.total_pixels == 100
    assert res.diff_pixels == 1
    assert res.diff_percentage == 1.0
    assert res.has_divergence is True
    assert diff_ppm.exists()
