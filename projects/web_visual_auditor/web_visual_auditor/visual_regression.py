"""Módulo de auditoria e regressão visual diferencial pixel a pixel.

Compara imagens (baseline vs current) com tolerância ajustável para variações
de antialiasing e renderização de fontes (padrão canal delta > 15), gerando
máscaras visuais de calor destacando os pixels alterados em vermelho puro (#FF0000).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from web_visual_auditor.exceptions import (
    ImageDimensionMismatchError,
    ImageLoadError,
    VisualRegressionError,
)
from web_visual_auditor.models import VisualDiffResult

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment]
    HAS_PIL = False


class PureImageBuffer:
    """Buffer de imagem em memória para fallback puro caso Pillow não esteja instalado."""

    def __init__(
        self,
        width: int,
        height: int,
        pixels: list[tuple[int, int, int]] | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.size = (width, height)
        if pixels is not None:
            self.pixels = pixels
        else:
            self.pixels = [(0, 0, 0)] * (width * height)

    def getdata(self) -> list[tuple[int, int, int]]:
        """Retorna todos os pixels RGB."""
        return self.pixels

    def getpixel(self, xy: tuple[int, int]) -> tuple[int, int, int]:
        """Obtém o pixel nas coordenadas (x, y)."""
        x, y = xy
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("Coordenada fora do limite da imagem.")
        return self.pixels[y * self.width + x]

    def putpixel(
        self,
        xy: tuple[int, int],
        color: tuple[int, int, int] | tuple[int, int, int, int],
    ) -> None:
        """Define o pixel nas coordenadas (x, y)."""
        x, y = xy
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("Coordenada fora do limite da imagem.")
        rgb = (color[0], color[1], color[2])
        self.pixels[y * self.width + x] = rgb

    def save_ppm(self, file_path: str | Path) -> None:
        """Salva a imagem no formato binário portátil Netpbm PPM (P6)."""
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        header = f"P6\n{self.width} {self.height}\n255\n".encode("ascii")
        byte_data = bytearray()
        for r, g, b in self.pixels:
            byte_data.extend((r, g, b))
        with open(target, "wb") as f:
            f.write(header)
            f.write(byte_data)


class VisualRegressionAuditor:
    """Motor de regressão visual diferencial pixel a pixel.

    Avalia alterações visuais entre duas capturas de tela, aplicando tolerância
    contra variações leves de antialiasing (canal > 15) e gerando máscaras de calor
    onde pixels divergentes são destacados em vermelho puro (#FF0000).
    """

    DEFAULT_TOLERANCE: int = 15

    def __init__(self, channel_tolerance: int = DEFAULT_TOLERANCE) -> None:
        """Inicializa o auditor com um limiar de tolerância por canal.

        Args:
            channel_tolerance: Variação máxima permitida por canal (R, G, B)
                sem que o pixel seja classificado como divergente. Padrão: 15.
        """
        if not (0 <= channel_tolerance <= 255):
            raise VisualRegressionError(
                f"Tolerância de canal deve estar entre 0 e 255, recebido: {channel_tolerance}"
            )
        self.channel_tolerance = channel_tolerance

    def _load_image(self, img_input: Any) -> tuple[Any, str]:
        """Carrega e normaliza uma imagem de arquivo ou objeto em memória.

        Retorna:
            Tupla contendo o objeto de imagem e o caminho canônico de origem.
        """
        if isinstance(img_input, (str, Path)):
            path_obj = Path(img_input)
            if not path_obj.exists():
                raise ImageLoadError(f"Arquivo de imagem não encontrado: '{path_obj}'")
            if not HAS_PIL:
                raise ImageLoadError(
                    "Pillow (PIL) não está disponível para decodificar arquivos de imagem do disco."
                )
            try:
                img = Image.open(path_obj)
                img.load()  # Garante leitura completa do buffer
                return img, str(path_obj)
            except Exception as exc:
                raise ImageLoadError(
                    f"Falha ao abrir ou decodificar a imagem '{path_obj}': {exc}"
                ) from exc

        # Se já for instância de PIL.Image.Image
        if HAS_PIL and isinstance(img_input, Image.Image):
            src_path = getattr(img_input, "filename", "memory://image") or "memory://image"
            return img_input, str(src_path)

        # Se for buffer puro
        if isinstance(img_input, PureImageBuffer):
            return img_input, "memory://pure_buffer"

        raise ImageLoadError(
            f"Tipo de imagem incompatível: {type(img_input)}. Esperado: Image.Image, Path ou str."
        )

    def compare_images(
        self,
        baseline_img: Any,
        current_img: Any,
        diff_output_path: str | Path | None = None,
        tolerance: int | None = None,
    ) -> VisualDiffResult:
        """Compara duas imagens e calcula as métricas exatas de divergência visual.

        Args:
            baseline_img: Imagem de referência (PIL.Image, Path ou caminho str).
            current_img: Imagem atual sob teste (PIL.Image, Path ou caminho str).
            diff_output_path: Caminho opcional onde a imagem diferencial será gravada.
            tolerance: Tolerância por canal sobrepondo a configuração padrão da instância.

        Returns:
            VisualDiffResult com percentual, contagem de pixels e metadados.

        Raises:
            ImageDimensionMismatchError: Se as imagens tiverem resoluções diferentes.
            ImageLoadError: Se houver falha ao carregar ou ler as imagens.
        """
        img_b, path_b = self._load_image(baseline_img)
        img_c, path_c = self._load_image(current_img)

        return self.compare_pixels(
            img_baseline=img_b,
            img_current=img_c,
            diff_output_path=diff_output_path,
            tolerance=tolerance,
            baseline_path=path_b,
            current_path=path_c,
        )

    def compare_pixels(
        self,
        img_baseline: Any,
        img_current: Any,
        diff_output_path: str | Path | None = None,
        tolerance: int | None = None,
        baseline_path: str = "memory://baseline",
        current_path: str = "memory://current",
    ) -> VisualDiffResult:
        """Executa a comparação matemática pixel a pixel com tolerância a antialiasing.

        Args:
            img_baseline: Imagem base normalizada.
            img_current: Imagem atual normalizada.
            diff_output_path: Caminho para gravação da máscara diferencial.
            tolerance: Limiar de tolerância delta por canal (padrão 15).
            baseline_path: Identificador ou caminho da baseline.
            current_path: Identificador ou caminho da current.

        Returns:
            Instância validada de VisualDiffResult.
        """
        tol = tolerance if tolerance is not None else self.channel_tolerance
        if not (0 <= tol <= 255):
            raise VisualRegressionError(f"Tolerância inválida: {tol}")

        # Validação estrita de dimensões
        size_b = getattr(img_baseline, "size", None)
        size_c = getattr(img_current, "size", None)

        if size_b is None or size_c is None or size_b != size_c:
            dims_b = size_b if size_b is not None else (0, 0)
            dims_c = size_c if size_c is not None else (0, 0)
            raise ImageDimensionMismatchError(
                baseline_dims=dims_b,
                current_dims=dims_c,
                message=f"Dimensões incompatíveis: baseline {dims_b} != current {dims_c}",
            )

        width, height = size_b
        total_pixels = width * height

        if total_pixels <= 0:
            raise VisualRegressionError("A resolução da imagem deve conter ao menos 1 pixel.")

        # Extração de dados RGB
        if HAS_PIL and isinstance(img_baseline, Image.Image):
            rgb_b = img_baseline.convert("RGB")
            rgb_c = img_current.convert("RGB")
            data_b = list(rgb_b.getdata())
            data_c = list(rgb_c.getdata())
        else:
            data_b = img_baseline.getdata()
            data_c = img_current.getdata()

        diff_pixels = 0
        diff_indices: list[int] = []

        # Algoritmo de verificação diferencial pixel a pixel com tolerância
        for idx in range(total_pixels):
            r1, g1, b1 = data_b[idx][:3]
            r2, g2, b2 = data_c[idx][:3]
            delta = max(abs(r1 - r2), abs(g1 - g2), abs(b1 - b2))
            if delta > tol:
                diff_pixels += 1
                diff_indices.append(idx)

        diff_percentage = (diff_pixels / total_pixels) * 100.0
        has_divergence = diff_pixels > 0

        # Definição do destino da imagem diferencial
        # Se fornecido um diff_output_path, sempre salva nele.
        # Se não fornecido mas houver divergência, salva por padrão em "diff_result.png".
        target_diff_path: str | None = None
        if diff_output_path is not None:
            target_diff_path = str(diff_output_path)
        elif has_divergence:
            target_diff_path = "diff_result.png"

        saved_diff_file: str | None = None

        if target_diff_path is not None:
            saved_diff_file = self._generate_and_save_diff_mask(
                width=width,
                height=height,
                data_baseline=data_b,
                diff_indices_set=set(diff_indices),
                target_path=target_diff_path,
            )

        return VisualDiffResult(
            baseline_path=baseline_path,
            current_path=current_path,
            diff_output_path=saved_diff_file,
            total_pixels=total_pixels,
            diff_pixels=diff_pixels,
            diff_percentage=round(diff_percentage, 6),
            has_divergence=has_divergence,
            channel_tolerance=tol,
            dimensions_match=True,
            baseline_dimensions=(width, height),
            current_dimensions=(width, height),
        )

    def _generate_and_save_diff_mask(
        self,
        width: int,
        height: int,
        data_baseline: list[tuple[int, int, int]],
        diff_indices_set: set[int],
        target_path: str,
    ) -> str:
        """Gera a máscara destacando pixels divergentes em vermelho puro (#FF0000).

        Pixels inalterados são renderizados com atenuação suave em escala de cinza
        para contextualização visual imediata.
        """
        dest_path = Path(target_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Cor de destaque: Vermelho puro #FF0000
        RED_HIGHLIGHT_RGBA = (255, 0, 0, 255)
        RED_HIGHLIGHT_RGB = (255, 0, 0)

        if HAS_PIL:
            mask_img = Image.new("RGBA", (width, height))
            pixels_out: list[tuple[int, int, int, int]] = []

            for idx in range(width * height):
                if idx in diff_indices_set:
                    pixels_out.append(RED_HIGHLIGHT_RGBA)
                else:
                    r, g, b = data_baseline[idx][:3]
                    # Tom de cinza suave atenuado para contexto de fundo
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    dim_gray = int(gray * 0.35 + 165 * 0.65)
                    pixels_out.append((dim_gray, dim_gray, dim_gray, 255))

            mask_img.putdata(pixels_out)
            # Salva no formato PNG
            mask_img.save(dest_path, format="PNG")
        else:
            # Fallback puro: salva em formato PPM ou arquivo puro
            pure_buf = PureImageBuffer(width, height)
            for idx in range(width * height):
                x = idx % width
                y = idx // width
                if idx in diff_indices_set:
                    pure_buf.putpixel((x, y), RED_HIGHLIGHT_RGB)
                else:
                    r, g, b = data_baseline[idx][:3]
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    dim_gray = int(gray * 0.35 + 165 * 0.65)
                    pure_buf.putpixel((x, y), (dim_gray, dim_gray, dim_gray))

            if str(dest_path).lower().endswith(".ppm"):
                pure_buf.save_ppm(dest_path)
            else:
                # Se extensão for PNG mas PIL não estiver instalado, grava PPM com extensão apropriada
                pure_buf.save_ppm(dest_path.with_suffix(".ppm"))

        return str(dest_path)


# Alias canônico para compatibilidade arquitetural
VisualRegressionEngine = VisualRegressionAuditor
