"""Roteador Inteligente e Classificador de Intenções (AutoSkillRouter)."""

import unicodedata
from typing import Any

from shared.logger import get_logger

logger = get_logger("AutoSkillRouter")

TRIGGERS = ("ativa brain", "brain prompt", "executar skill", "rotear")

TRIVIAL = {
    "oi",
    "ola",
    "olá",
    "bom dia",
    "boa tarde",
    "boa noite",
    "obrigado",
    "obrigada",
    "valeu",
    "ok",
    "tudo bem",
    "eai",
    "e ai",
}

DESTRUCTIVE_KEYWORDS = (
    "apagar",
    "deletar",
    "excluir",
    "remover tudo",
    "rm -rf",
    "del /",
    "formatar",
    "drop table",
    "drop database",
    "resetar tudo",
    "sobrescrever tudo",
)

COMPLEX_MARKERS = (
    "projeto",
    "mvp",
    "sistema completo",
    "app completo",
    "aplicativo completo",
    "do zero",
    "arquitetura completa",
    "plataforma",
    "ecossistema",
    "reorganizar",
    "migracao",
)

ROUTING_MATRIX: list[tuple[str, str, tuple[str, ...]]] = [
    # Governança & Auditoria
    ("code-validator", "auditoria", ("validar codigo", "analise de risco", "linha a linha", "auditar script")),
    ("skill-repo-analyser", "auditoria", ("pastas soltas", "reorganizar", "workspace", "migracao de codigo")),
    ("api-auditor", "auditoria", ("endpoint", "api", "url", "testar rota", "latencia api")),
    ("code-reviewer", "auditoria", ("code review", "revisar codigo", "qualidade de codigo", "checklist")),
    ("validacao-pre-entrega", "governanca", ("pre-entrega", "relatorio de ganho", "score de qualidade", "metricas")),
    ("skill-healthcheck", "governanca", ("saude do catalogo", "healthcheck", "auditar skills", "redundancia")),
    ("skill-factory", "governanca", ("criar skill", "nova skill", "padronizar skill", "fabricar skill")),
    ("resilience-circuit-breaker", "governanca", ("disjuntor", "circuit breaker", "loop", "deadlock")),
    ("skill-context-expander-guard", "governanca", ("organize meu pedido", "estruture este contexto", "melhore meu comando", "expanda esta ideia")),
    # Pesquisa & Conhecimento
    ("deep-research", "pesquisa", ("pesquisa profunda", "web search", "multi-fonte", "relatorio aprofundado")),
    ("notebooklm", "pesquisa", ("notebooklm", "caderno", "audio overview", "consultar notas")),
    ("skill-prompt-generator", "governanca", ("gerar prompt", "prompt engineering", "tags xml", "arquiteto de prompts")),
    # UI / Frontend
    ("frontend-design", "ui", ("design", "layout", "interface", "componente", "tailwind", "tela")),
    ("accessibility", "ui", ("acessibilidade", "a11y", "wcag", "aria", "contraste")),
    ("tactile-hyperreal-ui-auditor", "ui", ("tatil", "hiper-realista", "4k feel", "sombras", "acabamento premium")),
    ("color-palette-and-depth-architect", "ui", ("paleta de cores", "gradiente", "profundidade", "tema dark")),
    ("minimal-ui-menu-icon-architect", "ui", ("menu minimalista", "sidebar", "dock", "navbar", "icone svg")),
    ("responsive-html-ui-master", "ui", ("responsivo", "mobile-first", "menu movel", "html5")),
    ("skill-html-modular-builder", "ui", ("montagem de pages", "montagem html", "html modular", "pagina html", "construir tela html", "atomic design html")),
    ("design-interface-medica-minimalista", "medico", ("medico", "prontuario", "prescricao", "clinica", "cfm", "a4")),
    # Dados & Analytics
    ("workspace-data-analytics-architect", "dados", ("kpi", "dashboard", "metricas", "planilha", "chat analitico")),
    ("sql_specialist", "dados", ("sql", "bigquery", "query", "tabela", "schema")),
    ("workspace_specialist", "arquitetura", ("pastas", "diretorio", "arquivos locais", "scan")),
    ("html_modular_specialist", "ui", ("especialista html", "gerador html", "montador de componentes")),
]

# Alvos que identificam um subagente Python (agents/specialized/*), não um SKILL.md do catálogo.
# Usado para o orquestrador não injetar o nome do agente como se fosse conteúdo de skill.
AGENT_TARGETS = {"sql_specialist", "workspace_specialist", "html_modular_specialist", "research_evolution_specialist"}


def normalize_text(text: str | None) -> str:
    """Normaliza texto para minúsculas e sem acentos."""
    if text is None:
        return ""
    text = str(text).lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


class AutoSkillRouter:
    """Motor determinístico de classificação de intenções, complexidade e seleção de skills."""

    def __init__(self):
        self.matrix = ROUTING_MATRIX

    def score_entry(self, entry: str) -> list[tuple[str, str, list[str]]]:
        """Pontua e retorna [(skill, dominio, palavras_casadas)] ordenado por relevância."""
        results = []
        for skill, domain, keywords in self.matrix:
            hits = [kw for kw in keywords if normalize_text(kw) in entry]
            if hits:
                results.append((skill, domain, hits))
        results.sort(key=lambda r: len(r[2]), reverse=True)
        return results

    def classify_complexity(self, entry: str, raw: str, scored: list) -> str:
        """Classifica a complexidade da intenção do usuário."""
        if any(m in entry for m in COMPLEX_MARKERS):
            return "COMPLEXO"
        domains = {domain for _, domain, _ in scored}
        if len(domains) >= 3 or (len(domains) >= 2 and len(scored) >= 3):
            return "COMPLEXO"
        if len(raw.split()) <= 10 and len(scored) <= 1:
            return "SIMPLES"
        return "INTERMEDIARIO"

    def route(self, user_input: str | None) -> dict[str, Any]:
        """Calcula o roteamento da entrada."""
        raw = (user_input or "").strip()
        entry = normalize_text(raw)

        trigger_source = "FRASE_CHAVE" if any(t in entry for t in TRIGGERS) else "AUTOMATICO"

        # 1. Portão destrutivo (prioridade máxima)
        if any(d in entry for d in DESTRUCTIVE_KEYWORDS):
            return {
                "trigger_source": trigger_source,
                "detected_intent": raw,
                "complexity": "COMPLEXO",
                "target_skill": "accidental-data-loss-prevention",
                "target_type": "skill",
                "execution_mode": "HITL_BLOCK",
                "is_destructive": True,
                "next_action": "BLOQUEAR e solicitar confirmação explícita antes de qualquer mutação destrutiva.",
                "candidates": [],
            }

        # 2. Conversação trivial
        if trigger_source == "AUTOMATICO" and entry in TRIVIAL:
            return {
                "trigger_source": trigger_source,
                "detected_intent": raw,
                "complexity": "SIMPLES",
                "target_skill": None,
                "target_type": "none",
                "execution_mode": "DIRECT_RESPONSE",
                "is_destructive": False,
                "next_action": "Resposta direta conversacional sem injeção pesada de skills.",
                "candidates": [],
            }

        scored = self.score_entry(entry)
        complexity = self.classify_complexity(entry, raw, scored)

        if not scored:
            return {
                "trigger_source": trigger_source,
                "detected_intent": raw,
                "complexity": complexity,
                "target_skill": None,
                "target_type": "none",
                "execution_mode": "DIRECT_RESPONSE",
                "is_destructive": False,
                "next_action": "Resposta direta com apoio das diretrizes gerais.",
                "candidates": [],
            }

        if complexity == "COMPLEXO":
            mode = "MULTI_AGENT_CASCADE"
            target = "orchestrator"
        else:
            mode = "SINGLE_SKILL"
            target = scored[0][0]

        candidates = [
            {"skill": s, "domain": d, "matched_keywords": kw} for s, d, kw in scored[:4]
        ]

        target_type = "meta" if target == "orchestrator" else ("agent" if target in AGENT_TARGETS else "skill")

        return {
            "trigger_source": trigger_source,
            "detected_intent": raw,
            "complexity": complexity,
            "target_skill": target,
            "target_type": target_type,
            "execution_mode": mode,
            "is_destructive": False,
            "next_action": f"Execução via modo {mode} com foco em {target}.",
            "candidates": candidates,
        }
