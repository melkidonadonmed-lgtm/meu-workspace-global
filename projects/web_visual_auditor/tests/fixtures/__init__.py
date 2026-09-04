"""Módulo de inicialização do pacote de fixtures de teste."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent
SAMPLE_PAGE_HTML = FIXTURES_DIR / "sample_page.html"
SAMPLE_NOISY_ARTICLE_HTML = FIXTURES_DIR / "sample_noisy_article.html"

__all__ = [
    "FIXTURES_DIR",
    "SAMPLE_NOISY_ARTICLE_HTML",
    "SAMPLE_PAGE_HTML",
]
