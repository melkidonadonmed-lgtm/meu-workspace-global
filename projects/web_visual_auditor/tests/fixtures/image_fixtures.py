"""Módulo utilitário para geração determinística de fixtures de imagem sintéticas.

Este módulo provê construtores de pares de imagem (baseline vs current) com garantias
matemáticas estritas de divergência e conformidade com os requisitos de tolerância
a antialiasing (delta de canal > 15) estabelecidos em ORIGINAL_REQUEST.md (§R3).
"""

from pathlib import Path

from PIL import Image, ImageDraw


def generate_identical_pair(
    width: int = 100,
    height: int = 100,
    color: tuple[int, int, int] = (255, 255, 255),
) -> tuple[Image.Image, Image.Image]:
    """Gera um par de imagens perfeitamente idênticas (100x100, branco puro por padrão).

    Garantia matemática:
        different_pixels == 0
        diff_percentage == 0.0%
        has_diff == False
    """
    baseline = Image.new("RGB", (width, height), color)
    current = Image.new("RGB", (width, height), color)
    return baseline, current


def generate_subtle_noise_pair(
    width: int = 100,
    height: int = 100,
    base_color: tuple[int, int, int] = (255, 255, 255),
    noise_delta: int = 10,
) -> tuple[Image.Image, Image.Image]:
    """Gera um par com ruído leve de canal <= 15 (ex: branco 255 vs cinza 245).

    Simula variações aceitáveis de renderização e antialiasing de sub-pixel.

    Garantia matemática para qualquer limiar de tolerância >= 15:
        max(|c1 - c2|) == noise_delta <= 15
        different_pixels == 0
        diff_percentage == 0.0%
        has_diff == False
    """
    safe_noise = min(max(noise_delta, 0), 15)
    baseline = Image.new("RGB", (width, height), base_color)
    noisy_color = tuple(max(0, min(255, c - safe_noise)) for c in base_color)
    # Garante tipo tuple[int, int, int] para o PIL
    rgb_noisy = (int(noisy_color[0]), int(noisy_color[1]), int(noisy_color[2]))
    current = Image.new("RGB", (width, height), rgb_noisy)
    return baseline, current


def generate_divergent_square_pair(
    width: int = 100,
    height: int = 100,
    base_color: tuple[int, int, int] = (255, 255, 255),
    square_color: tuple[int, int, int] = (0, 0, 0),
    square_size: int = 20,
    top_left: tuple[int, int] = (40, 40),
) -> tuple[Image.Image, Image.Image]:
    """Gera um par com quadrado divergente controlado (delta canal > 15).

    Por padrão:
        - Imagem base: 100x100 pixels brancos (10.000 pixels no total).
        - Quadrado: 20x20 pixels na cor preta posicionado em (40, 40) a (59, 59).
        - Delta de canal: |255 - 0| = 255 > 15.

    Garantia matemática estrita:
        total_pixels == 10000
        different_pixels == 400 (20 * 20)
        diff_percentage == 4.0% (400 / 10000 * 100.0)
        has_diff == True
    """
    baseline = Image.new("RGB", (width, height), base_color)
    current = Image.new("RGB", (width, height), base_color)

    draw = ImageDraw.Draw(current)
    x0, y0 = top_left
    x1 = x0 + square_size - 1
    y1 = y0 + square_size - 1
    draw.rectangle([x0, y0, x1, y1], fill=square_color)

    return baseline, current


def generate_dimension_mismatch_pair(
    dim_a: tuple[int, int] = (100, 100),
    dim_b: tuple[int, int] = (120, 100),
    color_a: tuple[int, int, int] = (255, 255, 255),
    color_b: tuple[int, int, int] = (255, 255, 255),
) -> tuple[Image.Image, Image.Image]:
    """Gera par com dimensões divergentes para validar disparo de DimensionMismatchError."""
    img_a = Image.new("RGB", dim_a, color_a)
    img_b = Image.new("RGB", dim_b, color_b)
    return img_a, img_b


def save_image_pair_to_disk(
    baseline: Image.Image,
    current: Image.Image,
    output_dir: str | Path,
    baseline_filename: str = "baseline.png",
    current_filename: str = "current.png",
) -> tuple[Path, Path]:
    """Salva um par de imagens em formato PNG em um diretório temporário/alvo."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    baseline_path = target_dir / baseline_filename
    current_path = target_dir / current_filename

    baseline.save(baseline_path, format="PNG")
    current.save(current_path, format="PNG")

    return baseline_path, current_path


def reference_pixel_divergence(
    img_a: Image.Image,
    img_b: Image.Image,
    threshold: int = 15,
) -> tuple[int, int, float]:
    """Oráculo autoritativo de referência em Python puro para cálculo de divergência.

    Retorna:
        tuple[different_pixels, total_pixels, diff_percentage]
    """
    if img_a.size != img_b.size:
        msg = f"Dimensões incompatíveis: {img_a.size} != {img_b.size}"
        raise ValueError(msg)

    width, height = img_a.size
    total_pixels = width * height

    rgb_a = img_a.convert("RGB")
    rgb_b = img_b.convert("RGB")

    data_a = list(rgb_a.getdata())
    data_b = list(rgb_b.getdata())

    different_pixels = 0
    for (r1, g1, b1), (r2, g2, b2) in zip(data_a, data_b, strict=True):
        channel_delta = max(abs(r1 - r2), abs(g1 - g2), abs(b1 - b2))
        if channel_delta > threshold:
            different_pixels += 1

    diff_percentage = (different_pixels / total_pixels) * 100.0
    return different_pixels, total_pixels, diff_percentage


def verify_mathematical_guarantees() -> dict[str, bool]:
    """Valida internamente as propriedades matemáticas de todas as fixtures sintéticas."""
    # 1. Par idêntico
    b1, c1 = generate_identical_pair(100, 100)
    diff_px1, total_px1, pct1 = reference_pixel_divergence(b1, c1, threshold=15)
    cond1 = (diff_px1 == 0) and (total_px1 == 10000) and (pct1 == 0.0)

    # 2. Ruído leve <= 15
    b2, c2 = generate_subtle_noise_pair(100, 100, noise_delta=10)
    diff_px2, total_px2, pct2 = reference_pixel_divergence(b2, c2, threshold=15)
    cond2 = (diff_px2 == 0) and (total_px2 == 10000) and (pct2 == 0.0)

    # 3. Quadrado 20x20 divergente em base 100x100
    b3, c3 = generate_divergent_square_pair(100, 100, square_size=20, top_left=(40, 40))
    diff_px3, total_px3, pct3 = reference_pixel_divergence(b3, c3, threshold=15)
    cond3 = (diff_px3 == 400) and (total_px3 == 10000) and (abs(pct3 - 4.0) < 1e-6)

    return {
        "identical_pair_zero_diff": cond1,
        "subtle_noise_zero_diff": cond2,
        "divergent_square_exact_4_percent": cond3,
    }


if __name__ == "__main__":
    results = verify_mathematical_guarantees()
    for name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {name}")
