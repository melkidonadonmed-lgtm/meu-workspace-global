#!/usr/bin/env python3
"""Hook PreToolUse Global para o Antigravity.

Localização Central Canônica: C:\\Users\\melki\\.gemini\\scripts\\hooks\\pre_tool_guard.py
Intercepta chamadas de ferramentas propostas pelo modelo antes de sua execução.
Aplica políticas Zero-Trust e HITL (Human-in-the-Loop) em:
1. Comandos potencialmente destrutivos (rm, del, git reset --hard, force push, drop, etc.).
2. Edições e mutações em arquivos sensíveis (.env, id_rsa, chaves, credenciais).
3. Violações de fronteiras de diretórios (mutações fora de projetos em desenvolvimento).
"""

import json
import os
import re
import sys
from pathlib import Path

# Padrões de comandos destrutivos ou de alto risco
DESTRUCTIVE_COMMAND_PATTERNS = [
    r"(?i)\brm\s+-[rf]{1,2}\b",
    r"(?i)\brm\s+-[rf]\s+-[rf]\b",
    r"(?i)\bRemove-Item\b.*-Recurse",
    r"(?i)\bdel\s+/[sqf]\b",
    r"(?i)\brmdir\s+/[sq]\b",
    r"(?i)\bgit\s+reset\s+--hard\b",
    r"(?i)\bgit\s+clean\s+-[fdx]{1,3}\b",
    r"(?i)\bgit\s+clean\b.*-[fdx]",
    r"(?i)\bgit\s+push\b.*--force",
    r"(?i)\bgit\s+branch\s+-[dD]\b",
    r"(?i)\bdrop\s+(database|table)\b",
    r"(?i)\btruncate\s+table\b",
    r"(?i)\bformat\s+[a-z]:",
]

# Padrões de arquivos protegidos/sensíveis
SENSITIVE_FILE_PATTERNS = [
    r"(?i)\.env(\.[a-zA-Z0-9_-]+)?$",
    r"(?i)id_rsa(\.pub)?$",
    r"(?i)id_ed25519(\.pub)?$",
    r"(?i)\.pem$",
    r"(?i)\.key$",
    r"(?i)credentials\.json$",
    r"(?i)service[-_]account.*\.json$",
    r"(?i)token\.json$",
]


def is_path_in_allowed_target(target_str: str) -> tuple[bool, str]:
    """Verifica se o caminho de escrita está em uma zona autorizada para desenvolvimento autônomo."""
    if not target_str:
        return False, "Caminho de arquivo vazio ou inválido."

    try:
        p = Path(target_str)
        resolved = p.resolve()
    except Exception as err:
        return False, f"Falha na resolução do caminho '{target_str}': {err}"

    resolved_str = resolved.as_posix().lower()

    # 1. Zonas de projetos clientes em desenvolvimento (Projetos/* e junctions em meu-workspace-global/projects/*)
    if resolved_str.startswith("c:/users/melki/projetos"):
        return True, "Projeto cliente em desenvolvimento"

    # 2. Meta-workspace de desenvolvimento governado
    if resolved_str.startswith("c:/users/melki/meu-workspace-global"):
        # Proteção das skills governadas (requer aprovação explícita HITL)
        if resolved_str.startswith("c:/users/melki/meu-workspace-global/skills"):
            return False, f"Guardrail Zero-Trust: Edição em catálogo governado de skills ('{target_str}'). Confirmação humana explícita (HITL) requerida."
        return True, "Meta-workspace de desenvolvimento"

    # 3. Áreas efêmeras, scratch, artefatos do runtime e testes
    if "/.gemini/antigravity-cli/brain" in resolved_str:
        return True, "Artefato da sessão"

    if "appdata/local/temp" in resolved_str or "/.pytest_temp" in resolved_str or "/pytest_tmp" in resolved_str:
        return True, "Diretório temporário"

    # 4. Metadados e notas nas pastas dedicadas de subagentes (.agents/worker_*, .agents/orchestrator_*, etc.)
    if "c:/users/melki/.agents/" in resolved_str:
        parts = [part.lower() for part in resolved.parts]
        try:
            agents_idx = parts.index(".agents")
            if len(parts) > agents_idx + 2:
                subfolder = parts[agents_idx + 1]
                if subfolder not in ("skills", "config"):
                    return True, "Metadados de subagente"
        except ValueError:
            pass

    # Qualquer outro local (raiz de C:/Users/melki, .gemini global, system folders)
    return False, f"Guardrail Zero-Trust: Tentativa de mutação fora das fronteiras de desenvolvimento autorizadas ('{target_str}'). Confirmação humana explícita (HITL) requerida."


def evaluate_pre_tool(payload: dict) -> dict:
    """Avalia o payload de PreToolUse e emite a decisão de segurança."""
    tool_call = payload.get("toolCall", {})
    name = tool_call.get("name", "")
    args = tool_call.get("args", {})

    # 1. Avaliação para comandos de terminal (run_command)
    if name == "run_command":
        cmd = args.get("CommandLine", "")
        for pattern in DESTRUCTIVE_COMMAND_PATTERNS:
            if re.search(pattern, cmd):
                return {
                    "decision": "force_ask",
                    "reason": f"Guardrail Zero-Trust: Comando potencialmente destrutivo detectado ('{cmd}'). Confirmação humana explícita (HITL) requerida.",
                }
        return {"decision": "allow"}

    # 2. Avaliação para operações de escrita de arquivo
    if name in ("write_to_file", "replace_file_content", "multi_replace_file_content"):
        target = args.get("TargetFile", "")
        target_name = Path(target).name

        # 2.1 Checagem de arquivo sensível
        for pattern in SENSITIVE_FILE_PATTERNS:
            if re.search(pattern, target_name):
                return {
                    "decision": "force_ask",
                    "reason": f"Guardrail Zero-Trust: Operação sobre arquivo sensível ('{target_name}'). Confirmação humana explícita (HITL) requerida.",
                }

        # 2.2 Checagem de fronteiras de diretórios
        is_allowed, reason = is_path_in_allowed_target(target)
        if not is_allowed:
            return {
                "decision": "force_ask",
                "reason": reason,
            }

        return {"decision": "allow"}

    # Padrão para demais ferramentas
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
        result = evaluate_pre_tool(payload)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(
            json.dumps(
                {
                    "decision": "allow",
                    "reason": f"Fallback seguro ativado por erro interno no hook: {e}",
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
