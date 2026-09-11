#!/usr/bin/env python3
"""Hook PreInvocation para o Antigravity.

Injeta lembretes contextuais efêmeros e diretrizes de governança
antes de cada chamada ao modelo Gemini.
"""

import json
import sys


def evaluate_pre_invocation(payload: dict) -> dict:
    """Injeta diretrizes contextuais essenciais na primeira invocação da sessão."""
    invocation_num = payload.get("invocationNum", 0)

    # Na primeira invocação, reforça regras primárias de operação
    if invocation_num == 0:
        reminder = (
            "Diretrizes Ativas do Ecossistema (AGENTS.md & GEMINI.md):\n"
            "1. Idioma obrigatório: Português BR em todas as respostas e artefatos.\n"
            "2. Zero-Trust & HITL: Comandos destrutivos e edição de arquivos sensíveis exigem confirmação explícita.\n"
            "3. Manter consistência técnica e respeitar os limites de projeto (projects/*)."
        )
        return {"injectSteps": [{"ephemeralMessage": reminder}]}

    return {"injectSteps": []}


def main() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"injectSteps": []}))
            return

        payload = json.loads(raw_input)
        result = evaluate_pre_invocation(payload)
        print(json.dumps(result, ensure_ascii=False))
    except Exception:
        print(json.dumps({"injectSteps": []}))


if __name__ == "__main__":
    main()
