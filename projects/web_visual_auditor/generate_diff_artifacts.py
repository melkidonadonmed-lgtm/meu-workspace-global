"""Script autônomo para geração física imediata dos artefatos de mapa diferencial PNG.

Gera fisicamente em disco:
1. projects/web_visual_auditor/tests/diff_result.png (100x100, 20x20 vermelho #FF0000 em (40, 40), fundo cinza suave)
2. projects/web_visual_auditor/tests/diff_button_checkout.png (100x40, 20x20 vermelho #FF0000 em (10, 10))
3. projects/web_visual_auditor/diff_result.png
4. projects/web_visual_auditor/artifacts/diff_result.png
5. projects/web_visual_auditor/diff_button_checkout.png
6. projects/web_visual_auditor/artifacts/diff_button_checkout.png
"""

from __future__ import annotations

import sys
from pathlib import Path

# Garante importação limpa do pacote
PACKAGE_DIR = Path(__file__).resolve().parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from PIL import Image, ImageDraw

from web_visual_auditor.component_auditor import ComponentAuditor
from web_visual_auditor.models import ComponentSnapshot
from web_visual_auditor.visual_regression import VisualRegressionAuditor


def generate_all_png_artifacts() -> None:
    """Gera e persiste fisicamente em disco todos os arquivos PNG com máscaras reais."""
    tests_dir = PACKAGE_DIR / "tests"
    artifacts_dir = PACKAGE_DIR / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Gerando artefatos PNG em {PACKAGE_DIR}...")

    # --------------------------------------------------------------------------
    # 1. diff_result.png (100x100 pixels, divergência 20x20 em (40, 40) = 400 px)
    # --------------------------------------------------------------------------
    base_img = Image.new("RGB", (100, 100), (200, 200, 200))
    curr_img = Image.new("RGB", (100, 100), (200, 200, 200))
    draw_curr = ImageDraw.Draw(curr_img)
    # Quadrado divergente de (40, 40) a (59, 59): delta = |200 - 0| = 200 > 15
    draw_curr.rectangle([40, 40, 59, 59], fill=(0, 0, 0))

    auditor = VisualRegressionAuditor(channel_tolerance=15)
    diff_res_path = tests_dir / "diff_result.png"
    res = auditor.compare_images(base_img, curr_img, diff_output_path=diff_res_path)

    print(f"[+] diff_result.png gerado: {res.diff_pixels} pixels divergentes (esperado 400).")

    # Replica para artifacts/ e raiz do pacote
    img_bytes = diff_res_path.read_bytes()
    (artifacts_dir / "diff_result.png").write_bytes(img_bytes)
    (PACKAGE_DIR / "diff_result.png").write_bytes(img_bytes)

    # --------------------------------------------------------------------------
    # 2. diff_button_checkout.png (100x40 pixels, divergência 20x20 em (10, 10))
    # --------------------------------------------------------------------------
    btn_base = Image.new("RGB", (100, 40), (200, 200, 200))
    btn_curr = Image.new("RGB", (100, 40), (200, 200, 200))
    draw_btn = ImageDraw.Draw(btn_curr)
    # Quadrado de regressão de (10, 10) a (29, 29): 20x20 = 400 px
    draw_btn.rectangle([10, 10, 29, 29], fill=(0, 0, 0))

    base_tmp = tests_dir / "_temp_btn_base.png"
    curr_tmp = tests_dir / "_temp_btn_curr.png"
    btn_base.save(base_tmp)
    btn_curr.save(curr_tmp)

    snap_b = ComponentSnapshot(
        selector="button.checkout",
        dimensions=(100, 40),
        screenshot_path=str(base_tmp),
    )
    snap_c = ComponentSnapshot(
        selector="button.checkout",
        dimensions=(100, 40),
        screenshot_path=str(curr_tmp),
    )

    comp_auditor = ComponentAuditor()
    diff_comp_path = tests_dir / "diff_button_checkout.png"
    comp_report = comp_auditor.compare_component_snapshots(
        snap_b,
        snap_c,
        diff_output_path=diff_comp_path,
    )

    print(
        f"[+] diff_button_checkout.png gerado: "
        f"{comp_report.diff_result.diff_pixels if comp_report.diff_result else 0} pixels divergentes."
    )

    comp_bytes = diff_comp_path.read_bytes()
    (artifacts_dir / "diff_button_checkout.png").write_bytes(comp_bytes)
    (PACKAGE_DIR / "diff_button_checkout.png").write_bytes(comp_bytes)

    if base_tmp.exists():
        base_tmp.unlink()
    if curr_tmp.exists():
        curr_tmp.unlink()

    print("[SUCCESS] Todos os 6 arquivos binários PNG foram gerados e persistidos em disco!")


if __name__ == "__main__":
    generate_all_png_artifacts()
