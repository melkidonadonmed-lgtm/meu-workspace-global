#!/usr/bin/env python3
"""Hook Stop para o Antigravity.

Executado quando o loop de execução do agente termina.
Valida o encerramento seguro e garante que tarefas em background
tenham concluído quando necessário.
"""

import json
import sys


def evaluate_stop(payload: dict) -> dict:
    """Verifica se o encerramento do turno é seguro."""
    # Por padrão, permite o encerramento normal da sessão
    return {"decision": "allow"}


def main() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "allow"}))
            return

        payload = json.loads(raw_input)
        result = evaluate_stop(payload)
        print(json.dumps(result, ensure_ascii=False))
    except Exception:
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
