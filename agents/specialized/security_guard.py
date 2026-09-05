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


class ProjectBoundaryGuardrail:
    """Guardrail de fronteira de projetos e prevenção de loops de auto-auditoria (R2).

    Garante que auditorias técnicas e revisões de código sejam direcionadas
    estritamente a projetos em desenvolvimento (projects/*) e terminantemente
    bloqueadas sobre a raiz do meta-workspace, a pasta de agentes e o catálogo de skills.
    """

    DEFAULT_ALLOWED_ROOTS: ClassVar[list[str]] = [
        "projects/*",
        "projects/pcm",
        "projects/canvas_ide",
        "projects/keepdocs-workspace",
        "projects/WAOE",
    ]

    DEFAULT_PROHIBITED_TARGETS: ClassVar[list[str]] = [
        "agents",
        "agents/*",
        "skills",
        "skills/*",
        ".",
        "./",
        "meu-workspace-global",
    ]

    def __init__(
        self,
        workspace_root: str | Path | None = None,
        config_path: str | Path | None = None,
    ):
        self.workspace_root = (
            Path(workspace_root).resolve()
            if workspace_root
            else Path(__file__).resolve().parents[2]
        )
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.allowed_roots, self.prohibited_targets, self.fallback_mode = self._load_policy()

    def _load_policy(self) -> tuple[list[str], list[str], str]:
        """Carrega a política de escopo de auditoria do guardrails.yaml."""
        allowed = list(self.DEFAULT_ALLOWED_ROOTS)
        prohibited = list(self.DEFAULT_PROHIBITED_TARGETS)
        fallback = "reject"

        if yaml is not None and self.config_path.exists():
            try:
                data = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
                policy = data.get("audit_scope_policy", {})
                if policy:
                    allowed = policy.get("allowed_audit_roots", allowed)
                    prohibited = policy.get("prohibited_audit_targets", prohibited)
                    fallback = policy.get("default_target_fallback_mode", fallback)
            except Exception as e:  # noqa: BLE001
                logger.error(f"Erro ao carregar audit_scope_policy de {self.config_path}: {e}")

        return allowed, prohibited, fallback

    def validate_audit_target(self, target_path: str | Path) -> tuple[bool, str]:
        """Valida se o alvo de auditoria respeita a fronteira segura de projetos.

        Retorna:
            (True, "TARGET_ALLOWED: ...") se o alvo for permitido em projects/*.
            (False, "AUDIT_TARGET_PROHIBITED: ...") se o alvo for a raiz, agents ou skills.
            (False, "AUDIT_TARGET_OUT_OF_BOUNDS: ...") se estiver fora do escopo permitido.
        """
        import fnmatch

        target_raw = str(target_path).strip()
        target_norm = target_raw.replace("\\", "/").strip()
        target_lower = target_norm.lower().rstrip("/")
        ws_root_norm = str(self.workspace_root).replace("\\", "/").strip().rstrip("/")
        ws_root_lower = ws_root_norm.lower()

        # Resolução de caminho relativo ao workspace se for absoluto
        rel_target = target_lower
        if target_lower == ws_root_lower or target_norm in [".", "./", ""]:
            rel_target = "."
        elif target_lower.startswith(ws_root_lower + "/"):
            rel_target = target_lower[len(ws_root_lower) + 1 :]

        # 1. Checagem de alvos proibidos (Anti-Loop / Auto-auditoria)
        prohibited_exact = {".", "./", "", "meu-workspace-global", ws_root_lower, f"{ws_root_lower}/"}
        if rel_target in prohibited_exact:
            return (
                False,
                "AUDIT_TARGET_PROHIBITED: Auto-auditoria sobre a raiz do meta-workspace é expressamente proibida.",
            )

        if rel_target == "agents" or rel_target.startswith("agents/"):
            return (
                False,
                "AUDIT_TARGET_PROHIBITED: Auto-auditoria sobre a pasta de agentes (agents/) é terminantemente proibida.",
            )

        if rel_target == "skills" or rel_target.startswith("skills/"):
            return (
                False,
                "AUDIT_TARGET_PROHIBITED: Auditoria sobre o catálogo de habilidades (skills/) é terminantemente proibida.",
            )

        for pattern in self.prohibited_targets:
            p_clean = pattern.replace("\\", "/").lower().strip()
            if fnmatch.fnmatch(rel_target, p_clean) or fnmatch.fnmatch(target_lower, p_clean):
                return (
                    False,
                    f"AUDIT_TARGET_PROHIBITED: Alvo '{target_raw}' está explicitamente proibido pela política de auditoria.",
                )

        # 2. Checagem de alvos permitidos (Projects)
        if rel_target.startswith("projects/") or "/projects/" in target_lower:
            return True, f"TARGET_ALLOWED: Projeto '{target_raw}' em projects/ aprovado para auditoria."

        known_projects = {"pcm", "canvas_ide", "keepdocs-workspace", "waoe", "customer_issue_reviewer_go"}
        if rel_target in known_projects:
            return True, f"TARGET_ALLOWED: Projeto '{target_raw}' aprovado para auditoria."

        for pattern in self.allowed_roots:
            p_clean = pattern.replace("\\", "/").lower().strip()
            if fnmatch.fnmatch(rel_target, p_clean) or fnmatch.fnmatch(target_lower, p_clean):
                return True, f"TARGET_ALLOWED: Alvo '{target_raw}' aprovado pela política de auditoria."

        # 3. Fallback para alvos fora de escopo
        return (
            False,
            f"AUDIT_TARGET_OUT_OF_BOUNDS: Alvo '{target_raw}' fora de projects/* não é permitido para auditoria.",
        )


class SecurityGuardAgent:
    """Validador e sanitizador de entradas e saídas de agentes.

    Os padrões de bloqueio são carregados de ``configs/guardrails.yaml``;
    se o arquivo (ou o PyYAML) não estiver disponível, usa os padrões padrão.
    """

    DEFAULT_BLOCKED_PATTERNS: ClassVar[list[str]] = [
        r"(?i)ignore\s+(all\s+)?previous\s+(instructions|guidelines|rules|prompts)",
        r"(?i)disregard\s+(system\s+)?(prompt|instructions|rules)",
        r"(?i)reveal\s+(api\s*key|password|credential|secret)",
        r"(?i)dump\s+.*(credentials|passwords|keys|secrets)",
        r"(?i)sudo\s+rm\s+-rf",
    ]

    CPF_PATTERN = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    def __init__(self, strict_mode: bool = True, config_path: str | Path | None = None):
        self.strict_mode = strict_mode
        resolved_cfg = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.blocked_patterns = self._load_blocked_patterns(resolved_cfg)
        self.boundary_guardrail = ProjectBoundaryGuardrail(config_path=resolved_cfg)

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

    def validate_audit_target(self, target_path: str | Path) -> tuple[bool, str]:
        """Valida se o alvo de auditoria respeita a fronteira segura de projetos."""
        return self.boundary_guardrail.validate_audit_target(target_path)

