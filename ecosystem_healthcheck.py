"""Healthcheck determinístico do workspace/hub com suporte a CLI."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HealthcheckItem:
    category: str
    name: str
    status: str
    message: str


@dataclass(frozen=True)
class HealthcheckReport:
    is_healthy: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    items: list[HealthcheckItem]

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_healthy": self.is_healthy,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "items": [asdict(item) for item in self.items],
        }


def check_json_file(path: Path) -> tuple[bool, str]:
    """Valida se um arquivo JSON existe e possui sintaxe válida."""
    if not path.exists():
        return False, f"Arquivo JSON não encontrado: {path}"
    if not path.is_file():
        return False, f"Caminho JSON não é arquivo: {path}"

    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return False, f"JSON inválido: {path} ({err.msg})"

    return True, f"JSON válido: {path}"


def check_python_ast(path: Path) -> tuple[bool, str]:
    """Valida se um script Python existe e possui AST sintaticamente válida."""
    if not path.exists():
        return False, f"Arquivo Python não encontrado: {path}"
    if not path.is_file():
        return False, f"Caminho Python não é arquivo: {path}"

    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as err:
        return False, f"Erro de sintaxe AST: {path} (linha {err.lineno})"

    return True, f"AST 100% válida: {path}"


def check_hook_contract(
    hook_path: Path, payload: dict[str, Any], expected_field: str
) -> tuple[bool, str]:
    """Executa um hook Python e verifica se o contrato JSON esperado foi respeitado."""
    if not hook_path.exists():
        return False, f"Hook não encontrado: {hook_path}"
    if not hook_path.is_file():
        return False, f"Caminho de hook inválido: {hook_path}"

    proc = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        return False, f"Hook retornou código {proc.returncode}: {hook_path}"

    try:
        data = json.loads(proc.stdout.strip() or "{}")
    except json.JSONDecodeError as err:
        return False, f"Saída JSON inválida do hook: {hook_path} ({err.msg})"

    if expected_field not in data:
        return False, f"Campo obrigatório ausente no hook: {expected_field}"

    return True, f"Contrato de execução válido: {hook_path}"


# Alias de compatibilidade
test_hook_contract = check_hook_contract


def _repo_root_from(base_dir: Path | None) -> Path:
    if base_dir is not None:
        return base_dir
    return Path(__file__).resolve().parent


def run_hub_healthcheck(base_dir: Path | None = None) -> HealthcheckReport:
    """Executa um conjunto determinístico de verificações sobre o workspace local."""
    root = _repo_root_from(base_dir)
    items: list[HealthcheckItem] = []

    json_targets = [
        root / "mcp_config.json",
        root / "skills-lock.json",
        root / "configs" / "orchestration_routes_memory.json",
        root / ".agents" / "hooks.json",
        root / ".agents" / "skills.json",
        root / ".agents" / "mcp_config.json",
    ]
    for path in json_targets:
        ok, message = check_json_file(path)
        items.append(
            HealthcheckItem(
                category="Configurações JSON",
                name=path.name,
                status="OK" if ok else "FAIL",
                message=message,
            )
        )

    python_targets = [
        root / "scripts" / "hooks" / "pre_tool_guard.py",
        root / "scripts" / "hooks" / "post_tool_reporter.py",
        root / "scripts" / "hooks" / "pre_invocation_reminder.py",
        root / "scripts" / "hooks" / "stop_verifier.py",
    ]
    for path in python_targets:
        ok, message = check_python_ast(path)
        items.append(
            HealthcheckItem(
                category="Lifecycle Hooks",
                name=path.name,
                status="OK" if ok else "FAIL",
                message=message,
            )
        )

    hook_contract_ok, hook_contract_message = check_hook_contract(
        root / "scripts" / "hooks" / "pre_tool_guard.py",
        {"toolCall": {"name": "run_command", "args": {"CommandLine": "dir"}}},
        "decision",
    )
    items.append(
        HealthcheckItem(
            category="Lifecycle Hooks",
            name="pre_tool_guard.py contract",
            status="OK" if hook_contract_ok else "FAIL",
            message=hook_contract_message,
        )
    )

    passed_checks = sum(item.status == "OK" for item in items)
    total_checks = len(items)
    failed_checks = total_checks - passed_checks

    return HealthcheckReport(
        is_healthy=failed_checks == 0,
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        items=items,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Executa o ecosystem healthcheck.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    report = run_hub_healthcheck()

    if args.as_json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0 if report.is_healthy else 1

    print("ANTIGRAVITY ECOSYSTEM HEALTHCHECK")
    print(f"Status: {'HEALTHY' if report.is_healthy else 'UNHEALTHY'}")
    print(
        f"Checks: total={report.total_checks} ok={report.passed_checks} falhas={report.failed_checks}"
    )
    for item in report.items:
        print(f"[{item.status}] {item.category} :: {item.name} - {item.message}")

    return 0 if report.is_healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
