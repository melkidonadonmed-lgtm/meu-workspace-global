#!/usr/bin/env python3
"""Auditoria dos projetos em C:\\Users\\melki\\Projetos com relação a Git online e Baseline."""

import subprocess
import sys
from pathlib import Path

from scripts.verify_project_baseline import BaselineVerifier

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

projects = [
    Path(r"C:\Users\melki\Projetos\pcm"),
    Path(r"C:\Users\melki\Projetos\canvas_ide"),
    Path(r"C:\Users\melki\Projetos\keepdocs-workspace"),
    Path(r"C:\Users\melki\Projetos\WAOE"),
    Path(r"C:\Users\melki\Projetos\tactile-ui-studio"),
    Path(r"C:\Users\melki\Projetos\repositorio-projetos-melki"),
]

print("=" * 80)
print("🔍 RELATÓRIO DE SITUAÇÃO DO GIT ONLINE & BASELINE DOS PROJETOS ATUAIS")
print("=" * 80)

for p in projects:
    print(f"\n📁 PROJETO: {p.name}")
    print(f"   Caminho: {p}")
    if not p.exists():
        print("   ❌ Diretório não existe!")
        continue

    # 1. Checagem Git
    dot_git = p / ".git"
    if dot_git.exists():
        try:
            remote_res = subprocess.run(["git", "remote", "-v"], cwd=str(p), capture_output=True, text=True, timeout=5)
            branch_res = subprocess.run(["git", "branch", "--show-current"], cwd=str(p), capture_output=True, text=True, timeout=5)
            status_res = subprocess.run(["git", "status", "-s"], cwd=str(p), capture_output=True, text=True, timeout=5)
            
            # Checar git fetch e status contra upstream
            fetch_res = subprocess.run(["git", "fetch", "--dry-run"], cwd=str(p), capture_output=True, text=True, timeout=10)
            upstream_res = subprocess.run(["git", "status", "-uno"], cwd=str(p), capture_output=True, text=True, timeout=5)

            current_branch = branch_res.stdout.strip() or "(detached HEAD)"
            remotes = remote_res.stdout.strip()
            pending_changes = status_res.stdout.strip()

            print(f"   [Git Local] Branch: {current_branch}")
            if remotes:
                print(f"   [Git Remoto] Remotes configurados:\n      " + "\n      ".join(remotes.splitlines()))
            else:
                print("   ⚠️ [Git Remoto] Nenhum repositório remoto (origin) configurado!")

            # Analisar status contra remote
            status_lines = upstream_res.stdout.strip().splitlines()
            tracking_info = [line for line in status_lines if "branch is" in line.lower() or "diverged" in line.lower() or "up to date" in line.lower() or "ahead" in line.lower() or "behind" in line.lower()]
            if tracking_info:
                print(f"   [Git Situação Online] {tracking_info[0]}")
            else:
                print(f"   [Git Situação Online] {status_lines[1] if len(status_lines) > 1 else 'Status padrão'}")

            if pending_changes:
                count_pending = len(pending_changes.splitlines())
                print(f"   ⚠️ [Git Status] {count_pending} arquivo(s) modificado(s) localmente não commitados.")
            else:
                print("   ✅ [Git Status] Working tree limpo (sem modificações pendentes).")

        except Exception as e:
            print(f"   ❌ Erro ao consultar Git: {e}")
    else:
        print("   ⚠️ [Git] Repositório Git (.git) não inicializado nesta pasta!")

    # 2. Checagem Baseline
    verifier = BaselineVerifier(p)
    rep = verifier.verify_all()
    status_label = "✅ APROVADO" if rep["passed"] else "❌ REPROVADO"
    print(f"   📊 [Baseline Mínimo] Conformidade: {rep['score']}% ({rep['passed_checks']}/{rep['total_checks']} checagens) | {status_label}")

    fails = [r for r in rep["results"] if r["status"] == "FAIL"]
    warns = [r for r in rep["results"] if r["status"] == "WARN"]

    if fails:
        print("      Faltam os seguintes itens mandatórios:")
        for f in fails:
            print(f"        ❌ {f['item']}: {f['detail']}")
    if warns:
        print("      Recomendações e avisos:")
        for w in warns:
            print(f"        ⚠️  {w['item']}: {w['detail']}")

print("\n" + "=" * 80)
