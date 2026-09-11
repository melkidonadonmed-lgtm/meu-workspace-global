#!/usr/bin/env python3
"""Hook PostToolUse para o Antigravity.

Executado imediatamente após a conclusão de uma ferramenta.
Permite registrar diagnósticos ou telemetria pós-execução.
Retorna sempre um objeto JSON vazio conforme o contrato da especificação.
"""

import json
import sys


def main() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        raw_input = sys.stdin.read()
        if raw_input.strip():
            _payload = json.loads(raw_input)
            # Pode registrar logs de erro em caso de necessidade futura:
            # error = _payload.get("error")
    except Exception:
        pass

    # Contrato oficial do PostToolUse: sempre retornar {}
    print(json.dumps({}))


if __name__ == "__main__":
    main()
