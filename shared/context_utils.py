"""Utilitários de gestão de contexto, cálculo aproximado de tokens e sanitização."""

from typing import Any


class TokenBudgetManager:
    """Gerenciador de orçamento de tokens para orquestração de contexto enxuto."""

    def __init__(self, max_tokens: int = 1_000_000, turn_budget: int = 50_000):
        self.max_tokens = max_tokens
        self.turn_budget = turn_budget
        self._current_usage = 0

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimativa rápida de tokens (aprox. 1 token = ~4 caracteres ou ~0.75 palavras)."""
        if not text:
            return 0
        # Média refinada para português e código
        return max(1, len(text) // 3)

    def is_within_budget(self, text: str) -> bool:
        """Verifica se o texto estimado cabe no orçamento da rodada."""
        return self.estimate_tokens(text) <= self.turn_budget

    def record_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Registra o consumo de tokens reportado pelo modelo."""
        self._current_usage += (prompt_tokens + completion_tokens)

    @property
    def total_used(self) -> int:
        return self._current_usage


def truncate_context(text: str, max_chars: int = 12000, suffix: str = "\n...[CONTEÚDO TRUNCADO PARA PREVENÇÃO DE CONTEXT BLOAT]...") -> str:
    """Trunca textos extensos mantendo as partes mais relevantes (início e fim)."""
    if not text:
        return text
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text

    safe_suffix = suffix if len(suffix) < max_chars else suffix[: max_chars // 2]
    safe_max = max(1, max_chars - len(safe_suffix))
    half = safe_max // 2
    return text[:half] + safe_suffix + text[-half:]


def extract_skills_summary(skills_metadata: list[dict[str, Any]]) -> str:
    """Formata um resumo enxuto de metadados de skills para injeção no prompt inicial (Progressive Disclosure)."""
    lines = ["## Habilidades Modulares Disponíveis (Carregadas sob Demanda):"]
    for s in skills_metadata:
        name = s.get("name", "sem-nome")
        desc = s.get("description", "Sem descrição disponível")
        lines.append(f"- **{name}**: {desc}")
    return "\n".join(lines)
