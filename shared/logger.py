"""Sistema unificado de logging estruturado e observabilidade."""

import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any, ClassVar


class JSONFormatter(logging.Formatter):
    """Formatador de log estruturado em JSON para observabilidade e telemetria."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data"):
            log_obj["extra"] = record.extra_data
        return json.dumps(log_obj, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Formatador legível para console com cores ANSI."""

    COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": "\033[36m",    # Ciano
        "INFO": "\033[32m",     # Verde
        "WARNING": "\033[33m",  # Amarelo
        "ERROR": "\033[31m",    # Vermelho
        "CRITICAL": "\033[41m", # Fundo Vermelho
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        time_str = datetime.now(UTC).astimezone().strftime("%H:%M:%S")
        prefix = f"{color}[{time_str} {record.levelname:<7} {record.name}]{self.RESET}"
        return f"{prefix} {record.getMessage()}"


def setup_logging(
    level: str | None = None,
    json_format: bool = False
) -> None:
    """Configura o logger raiz do sistema."""
    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Evita duplicidade de handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(numeric_level)
        if json_format:
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(ColoredConsoleFormatter())
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Obtém uma instância nomeada de logger devidamente configurada."""
    if not logging.getLogger().handlers:
        setup_logging()
    return logging.getLogger(name)
