"""Hierarquia de exceções especializadas para o pacote web_visual_auditor.

Todas as exceções derivam de AuditorError para permitir captura genérica ou
tratamento granular por subsistema.
"""

from __future__ import annotations


class AuditorError(Exception):
    """Exceção base para todos os erros do web_visual_auditor."""

    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)
        self.message = message

    def __str__(self) -> str:
        return self.message


class WebVisualAuditorError(AuditorError):
    """Alias/subclasse base canônica para compatibilidade arquitetural."""


class ResearchError(AuditorError):
    """Erros relacionados ao subsistema de pesquisa e recuperação web."""


class SemanticExtractionError(ResearchError):
    """Falha na extração semântica, limpeza de HTML ou parsing."""


class DOMAuditError(AuditorError):
    """Erros durante a inspeção de DOM e avaliação headless."""


class NavigationTimeoutError(DOMAuditError):
    """Timeout ao navegar ou carregar página web ou recurso local."""


class PageNavigationTimeoutError(NavigationTimeoutError):
    """Alias para erros de timeout de navegação de página."""


class ElementNotFoundError(DOMAuditError):
    """Elemento ou seletor CSS obrigatório não encontrado no DOM."""

    def __init__(self, selector: str, message: str | None = None) -> None:
        msg = message or f"Elemento não encontrado para o seletor CSS: '{selector}'"
        super().__init__(msg)
        self.selector = selector


class VisualRegressionError(AuditorError):
    """Erros no subsistema de auditoria e regressão visual."""


class ImageDimensionMismatchError(VisualRegressionError):
    """Incompatibilidade estrita entre dimensões de baseline e current."""

    def __init__(
        self,
        baseline_dims: tuple[int, int],
        current_dims: tuple[int, int],
        message: str | None = None,
    ) -> None:
        msg = (
            message
            or f"Dimensões incompatíveis: baseline {baseline_dims} vs current {current_dims}"
        )
        super().__init__(msg)
        self.baseline_dims = baseline_dims
        self.current_dims = current_dims


class ImageLoadError(VisualRegressionError):
    """Falha ao carregar, abrir ou decodificar arquivo de imagem."""


class ComponentAuditError(AuditorError):
    """Falha durante o isolamento, recorte ou auditoria de micro-componente."""


class ConfigurationError(AuditorError):
    """Erro de configuração ou parâmetros inválidos passados à suíte."""
