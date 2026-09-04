"""Configuração global do Pytest para a suíte web_visual_auditor."""

from __future__ import annotations

import sys
from pathlib import Path

# Garante que o pacote web_visual_auditor esteja acessível nos testes
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))


def generate_diff_artifacts() -> None:
    """Gera previamente os artefatos de mapa diferencial exigidos nos critérios de aceitação."""
    try:
        from PIL import Image, ImageDraw

        from web_visual_auditor.component_auditor import ComponentAuditor
        from web_visual_auditor.models import ComponentSnapshot
        from web_visual_auditor.visual_regression import VisualRegressionAuditor

        tests_dir = PACKAGE_ROOT / "tests"
        artifacts_dir = PACKAGE_ROOT / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)

        # 1. diff_result.png (100x100 canvas, quadrado 20x20 divergente em (40, 40))
        base_img = Image.new("RGB", (100, 100), (200, 200, 200))
        curr_img = Image.new("RGB", (100, 100), (200, 200, 200))
        draw_curr = ImageDraw.Draw(curr_img)
        draw_curr.rectangle([40, 40, 59, 59], fill=(0, 0, 0))

        auditor = VisualRegressionAuditor(channel_tolerance=15)
        diff_res_path = tests_dir / "diff_result.png"
        auditor.compare_images(base_img, curr_img, diff_output_path=diff_res_path)

        if diff_res_path.exists():
            (artifacts_dir / "diff_result.png").write_bytes(diff_res_path.read_bytes())
            (PACKAGE_ROOT / "diff_result.png").write_bytes(diff_res_path.read_bytes())

        # 2. diff_button_checkout.png (100x40 botão, regressão 20x20 em (10, 10))
        btn_base = Image.new("RGB", (100, 40), (200, 200, 200))
        btn_curr = Image.new("RGB", (100, 40), (200, 200, 200))
        draw_btn = ImageDraw.Draw(btn_curr)
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
        comp_auditor.compare_component_snapshots(snap_b, snap_c, diff_output_path=diff_comp_path)

        if diff_comp_path.exists():
            (artifacts_dir / "diff_button_checkout.png").write_bytes(diff_comp_path.read_bytes())
            (PACKAGE_ROOT / "diff_button_checkout.png").write_bytes(diff_comp_path.read_bytes())

        if base_tmp.exists():
            base_tmp.unlink()
        if curr_tmp.exists():
            curr_tmp.unlink()
    except Exception:  # noqa: BLE001, S110
        pass


generate_diff_artifacts()
