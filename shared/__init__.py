"""Fachada lazy para utilitários globais compartilhados do ecossistema."""

from importlib import import_module
from typing import Any

_EXPORTS: dict[str, str] = {
    "TokenBudgetManager": "shared.context_utils",
    "extract_skills_summary": "shared.context_utils",
    "get_logger": "shared.logger",
    "setup_logging": "shared.logger",
    "truncate_context": "shared.context_utils",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted((*globals(), *__all__))
