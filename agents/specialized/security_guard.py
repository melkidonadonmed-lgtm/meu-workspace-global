"""Agente Especialista em Segurança e Guardrails Zero-Trust (OWASP LLM01)."""

import re
from pathlib import Path
from typing import Any, ClassVar

from shared.logger import get_logger

logger = get_logger("SecurityGuard")

try:
    import yaml
except ImportError:
    yaml = None

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "guardrails.yaml"


class SecurityGuardAgent:
    """Validador e sanitizador de entradas e saídas de agentes.

    Os padrões de bloqueio são carregados de ``configs/guardrails.yaml``;
    se o arquivo (ou o PyYAML) não estiver disponível, usa os padrões padrão.
    """

    DEFAULT_BLOCKED_PATTERNS: ClassVar[list[str]] = [
        r"(?i)ignore previous instructions",
        r"(?i)disregard system prompt",
        r"(?i)reveal api key",
        r"(?i)dump credentials",
        r"(?i)sudo rm -rf",
    ]

    CPF_PATTERN = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    def __init__(self, strict_mode: bool = True, config_path: str | Path | None = None):
        self.strict_mode = strict_mode
        self.blocked_patterns = self._load_blocked_patterns(
            Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        )

    def _load_blocked_patterns(self, config_path: Path) -> list[str]:
        """Carrega os padrões de bloqueio do guardrails.yaml, com fallback aos padrões padrão."""
        if yaml is None or not config_path.exists():
            logger.warning(
                f"Guardrails indisponível ({config_path}). Usando padrões de bloqueio padrão."
            )
            return list(self.DEFAULT_BLOCKED_PATTERNS)

        try:
            data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            patterns = data.get("prompt_injection_protection", {}).get("blocked_patterns", [])
            if patterns:
                logger.info(
                    f"Guardrails carregados de {config_path.name}: {len(patterns)} padrões de bloqueio."
                )
                return [str(p) for p in patterns]
        except (OSError, yaml.YAMLError) as e:
            logger.error(f"Falha ao ler {config_path}: {e}. Usando padrões padrão.")

        return list(self.DEFAULT_BLOCKED_PATTERNS)

    def audit_input(self, user_text: str) -> dict[str, Any]:
        """Verifica a presença de tentativas de prompt injection e conteúdo malicioso."""
        for pattern in self.blocked_patterns:
            if re.search(pattern, user_text):
                logger.warning(f"Tentativa de injeção de prompt detectada com padrão: {pattern}")
                return {
                    "is_safe": False,
                    "reason": "Tentativa de injeção de prompt ou instrução não autorizada bloqueada pelos Guardrails.",
                    "sanitized_text": ""
                }

        sanitized = self._mask_pii(user_text)
        return {
            "is_safe": True,
            "reason": "Entrada validada com sucesso.",
            "sanitized_text": sanitized
        }

    def _mask_pii(self, text: str) -> str:
        """Mascara informações de identificação pessoal (PII)."""
        text = re.sub(self.CPF_PATTERN, "[CPF_MASCARADO]", text)
        text = re.sub(self.EMAIL_PATTERN, "[EMAIL_MASCARADO]", text)
        return text

    def audit_output(self, output_text: str) -> dict[str, Any]:
        """Garante que respostas geradas não vazem chaves ou dados confidenciais."""
        # Detecta potenciais API keys (ex: AIzaSy...)
        if re.search(r"AIza[0-9A-Za-z-_]{35}", output_text):
            logger.critical("Vazamento de chave de API interceptado na saída do modelo!")
            output_text = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[API_KEY_REDACTED]", output_text)

        return {
            "is_safe": True,
            "output_text": output_text
        }
