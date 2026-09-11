"""Testes unitários para os Lifecycle Hooks e scripts do Antigravity."""

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SCRIPTS_DIR = Path(r"C:\Users\melki\.gemini\scripts\hooks")
SCRIPTS_DIR = CANONICAL_SCRIPTS_DIR if CANONICAL_SCRIPTS_DIR.exists() else (WORKSPACE_ROOT / "scripts" / "hooks")


def _run_hook(script_name: str, payload: dict) -> dict:
    """Executa um script de hook passando JSON via stdin e capturando stdout."""
    script_path = SCRIPTS_DIR / script_name
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        input=json.dumps(payload),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return json.loads(proc.stdout.strip())


def test_pre_tool_guard_destructive_commands():
    """Valida se comandos destrutivos disparam force_ask."""
    destructive_commands = [
        "rm -rf /",
        "rm -r node_modules",
        "Remove-Item -Path C:/temp -Recurse",
        "del /s /q test",
        "git reset --hard HEAD~1",
        "git push origin main --force",
        "git branch -D feature-temp",
        "DROP TABLE users;",
        "TRUNCATE TABLE logs;",
    ]

    for cmd in destructive_commands:
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": cmd},
            }
        }
        res = _run_hook("pre_tool_guard.py", payload)
        assert res.get("decision") == "force_ask", f"Falhou para comando: {cmd}"
        assert "Guardrail Zero-Trust" in res.get("reason", "")


def test_pre_tool_guard_safe_commands():
    """Valida se comandos seguros são permitidos com allow."""
    safe_commands = [
        "git status",
        "git log -n 5",
        "npm test",
        "uv run pytest tests/unit/",
        "python --version",
        "dir",
    ]

    for cmd in safe_commands:
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": cmd},
            }
        }
        res = _run_hook("pre_tool_guard.py", payload)
        assert res.get("decision") == "allow", f"Falhou para comando: {cmd}"


def test_pre_tool_guard_sensitive_files():
    """Valida se escrita em arquivos sensíveis dispara force_ask."""
    sensitive_targets = [
        ".env",
        ".env.production",
        "id_rsa",
        "server.pem",
        "credentials.json",
        "service_account.json",
    ]

    for target in sensitive_targets:
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": f"C:/Users/melki/{target}"},
            }
        }
        res = _run_hook("pre_tool_guard.py", payload)
        assert res.get("decision") == "force_ask", f"Falhou para alvo sensível: {target}"

    # Arquivo comum deve ser permitido
    normal_payload = {
        "toolCall": {
            "name": "write_to_file",
            "args": {"TargetFile": "C:/Users/melki/meu-workspace-global/src/app.py"},
        }
    }
    res_normal = _run_hook("pre_tool_guard.py", normal_payload)
    assert res_normal.get("decision") == "allow"


def test_pre_tool_guard_directory_boundaries():
    """Valida se tentativas de mutação fora de projetos autorizados disparam force_ask."""
    # 1. Alvos fora do escopo de desenvolvimento (devem exigir confirmação humana explícita)
    unauthorized_targets = [
        "C:/Users/melki/bypass.txt",
        "C:/Users/melki/root_leak.py",
        "C:/Windows/System32/drivers/etc/hosts",
        "C:/Users/melki/.gemini/config/hooks.json",
        "C:/Users/melki/.agents/hooks.json",
        "C:/Users/melki/meu-workspace-global/skills/analytics/SKILL.md",
    ]

    for target in unauthorized_targets:
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": target},
            }
        }
        res = _run_hook("pre_tool_guard.py", payload)
        assert res.get("decision") == "force_ask", f"Deveria bloquear/pedir autorização para: {target}"
        assert "Guardrail Zero-Trust" in res.get("reason", "")

    # 2. Alvos autorizados (projetos clientes e desenvolvimento local)
    authorized_targets = [
        "C:/Users/melki/Projetos/pcm/src/App.tsx",
        "C:/Users/melki/Projetos/canvas_ide/index.html",
        "C:/Users/melki/meu-workspace-global/projects/pcm/src/main.ts",
        "C:/Users/melki/meu-workspace-global/src/app.py",
        "C:/Users/melki/meu-workspace-global/tests/unit/test_demo.py",
        "C:/Users/melki/.agents/worker_m1/notes.md",
    ]

    for target in authorized_targets:
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": target},
            }
        }
        res = _run_hook("pre_tool_guard.py", payload)
        assert res.get("decision") == "allow", f"Deveria permitir: {target}, erro: {res.get('reason')}"


def test_pre_invocation_reminder():
    """Valida injeção contextual de diretrizes em PreInvocation."""
    # Turno inicial (invocationNum == 0)
    payload_first = {"invocationNum": 0, "initialNumSteps": 0}
    res_first = _run_hook("pre_invocation_reminder.py", payload_first)
    assert "injectSteps" in res_first
    assert len(res_first["injectSteps"]) == 1
    assert "Português BR" in res_first["injectSteps"][0]["ephemeralMessage"]

    # Turno subsequente (invocationNum > 0)
    payload_next = {"invocationNum": 1, "initialNumSteps": 5}
    res_next = _run_hook("pre_invocation_reminder.py", payload_next)
    assert res_next == {"injectSteps": []}


def test_post_tool_reporter():
    """Valida conformidade do retorno do PostToolUse."""
    payload = {"stepIdx": 3, "error": ""}
    res = _run_hook("post_tool_reporter.py", payload)
    assert res == {}


def test_stop_verifier():
    """Valida retorno do hook de Stop."""
    payload = {"executionNum": 1, "terminationReason": "model_stop", "fullyIdle": True}
    res = _run_hook("stop_verifier.py", payload)
    assert res.get("decision") == "allow"


def test_hooks_json_schema():
    """Valida que todos os hooks.json no ambiente são JSONs válidos."""
    hook_paths = [
        Path(r"C:\Users\melki\.agents\hooks.json"),
        WORKSPACE_ROOT / ".agents" / "hooks.json",
        WORKSPACE_ROOT / "plugins" / "antigravity-governance" / "hooks.json",
    ]

    for p in hook_paths:
        assert p.exists(), f"Arquivo não encontrado: {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        for conf in data.values():
            assert "enabled" in conf or any(
                k in conf for k in ("PreToolUse", "PostToolUse", "PreInvocation", "Stop")
            )
