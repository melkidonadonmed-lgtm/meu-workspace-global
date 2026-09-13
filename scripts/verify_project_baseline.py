#!/usr/bin/env python3
"""
Validador de Baseline Mínimo Universal para Projetos (GitHub, Deploy & Produção).

Inspeciona o diretório de um projeto e valida a conformidade com a estrutura de pastas,
arquivos mandatórios de documentação, CI/CD, Git, segurança e qualidade de código.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class BaselineVerifier:
    def __init__(self, project_path: Path):
        self.project_path = project_path.resolve()
        self.results: list[dict[str, Any]] = []

    def _record(self, category: str, item: str, status: str, detail: str) -> None:
        self.results.append({
            "category": category,
            "item": item,
            "status": status,  # "PASS", "FAIL", "WARN"
            "detail": detail,
        })

    def verify_all(self) -> dict[str, Any]:
        if not self.project_path.exists() or not self.project_path.is_dir():
            return {
                "project_path": str(self.project_path),
                "error": "Diretório do projeto não existe ou não é uma pasta válida.",
                "passed": False,
                "score": 0,
                "results": [],
            }

        self._check_folder_structure()
        self._check_documentation()
        self._check_git_and_github()
        self._check_ci_cd()
        self._check_security_and_config()
        self._check_code_quality()

        total = len(self.results)
        passed_count = sum(1 for r in self.results if r["status"] == "PASS")
        score = int((passed_count / total) * 100) if total > 0 else 0
        all_mandatory_passed = all(
            r["status"] != "FAIL" for r in self.results
        )

        return {
            "project_path": str(self.project_path),
            "score": score,
            "passed": all_mandatory_passed,
            "total_checks": total,
            "passed_checks": passed_count,
            "results": self.results,
        }

    def _check_folder_structure(self) -> None:
        # src/
        src_candidates = ["src", "lib", "app", "pkg"]
        has_src = any((self.project_path / c).is_dir() for c in src_candidates)
        if has_src:
            self._record("Estrutura", "Diretório de Código-Fonte (src/)", "PASS", "Pasta de código encontrada.")
        else:
            self._record("Estrutura", "Diretório de Código-Fonte (src/)", "FAIL", "Nenhuma pasta de código-fonte (src, lib, app, pkg) encontrada.")

        # tests/
        test_candidates = ["tests", "test", "__tests__", "spec"]
        has_tests = any((self.project_path / c).is_dir() for c in test_candidates)
        if has_tests:
            self._record("Estrutura", "Diretório de Testes (tests/)", "PASS", "Pasta de testes encontrada.")
        else:
            self._record("Estrutura", "Diretório de Testes (tests/)", "WARN", "Pasta de testes não encontrada na raiz.")

        # docs/
        has_docs = (self.project_path / "docs").is_dir()
        self._record("Estrutura", "Diretório de Documentação (docs/)", "PASS" if has_docs else "WARN",
                     "Pasta docs/ presente." if has_docs else "Pasta docs/ opcional ausente.")

        # scripts/
        has_scripts = (self.project_path / "scripts").is_dir()
        self._record("Estrutura", "Diretório de Scripts (scripts/)", "PASS" if has_scripts else "WARN",
                     "Pasta scripts/ presente." if has_scripts else "Pasta scripts/ ausente.")

    def _check_documentation(self) -> None:
        # README.md
        readme = self.project_path / "README.md"
        if readme.is_file():
            content = readme.read_text(encoding="utf-8", errors="ignore").lower()
            missing_sections = []
            if not any(k in content for k in ["objetivo", "overview", "sobre", "about"]):
                missing_sections.append("objetivo")
            if not any(k in content for k in ["como rodar", "getting started", "instalação", "setup"]):
                missing_sections.append("como rodar local")
            if not any(k in content for k in ["test", "como testar"]):
                missing_sections.append("como testar")

            if missing_sections:
                self._record("Documentação", "README.md Completo", "WARN",
                             f"README existe mas pode carecer de: {', '.join(missing_sections)}.")
            else:
                self._record("Documentação", "README.md Completo", "PASS", "README.md contém seções essenciais.")
        else:
            self._record("Documentação", "README.md", "FAIL", "Arquivo README.md ausente.")

        # CHANGELOG.md
        changelog = self.project_path / "CHANGELOG.md"
        if changelog.is_file():
            self._record("Documentação", "CHANGELOG.md", "PASS", "CHANGELOG.md presente.")
        else:
            self._record("Documentação", "CHANGELOG.md", "FAIL", "Arquivo CHANGELOG.md ausente.")

        # CONTRIBUTING.md
        contributing = self.project_path / "CONTRIBUTING.md"
        if contributing.is_file():
            self._record("Documentação", "CONTRIBUTING.md", "PASS", "CONTRIBUTING.md presente.")
        else:
            self._record("Documentação", "CONTRIBUTING.md", "WARN", "Arquivo CONTRIBUTING.md ausente.")

    def _check_git_and_github(self) -> None:
        # .gitignore
        gitignore = self.project_path / ".gitignore"
        if gitignore.is_file():
            self._record("Git/GitHub", ".gitignore", "PASS", ".gitignore presente.")
        else:
            self._record("Git/GitHub", ".gitignore", "FAIL", ".gitignore ausente.")

        # PR Template
        pr_template_candidates = [
            self.project_path / ".github" / "PULL_REQUEST_TEMPLATE.md",
            self.project_path / ".github" / "pull_request_template.md",
            self.project_path / "PULL_REQUEST_TEMPLATE.md",
        ]
        has_pr_template = any(p.is_file() for p in pr_template_candidates)
        if has_pr_template:
            self._record("Git/GitHub", "Template de Pull Request", "PASS", "Template de PR configurado.")
        else:
            self._record("Git/GitHub", "Template de Pull Request", "WARN", "Template de PR ausente em .github/.")

        # Issue Templates
        issue_template_dir = self.project_path / ".github" / "ISSUE_TEMPLATE"
        if issue_template_dir.is_dir() and any(issue_template_dir.iterdir()):
            self._record("Git/GitHub", "Template de Issues", "PASS", "Templates de Issue encontrados.")
        else:
            self._record("Git/GitHub", "Template de Issues", "WARN", "Pasta .github/ISSUE_TEMPLATE/ ausente ou vazia.")

        # Git Status & Remoto
        dot_git = self.project_path / ".git"
        is_git_repo = dot_git.exists()
        if not is_git_repo:
            try:
                proc_inside = subprocess.run(
                    ["git", "rev-parse", "--is-inside-work-tree"],
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if proc_inside.stdout.strip() == "true":
                    is_git_repo = True
            except (subprocess.SubprocessError, OSError):
                pass

        if is_git_repo:
            try:
                proc_remote = subprocess.run(
                    ["git", "remote", "-v"],
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                remotes = proc_remote.stdout.strip()
                if remotes:
                    first_remote = remotes.splitlines()[0]
                    self._record("Git/GitHub", "Situação Git Online / Remoto", "PASS", f"Remoto configurado: {first_remote}")
                else:
                    self._record("Git/GitHub", "Situação Git Online / Remoto", "WARN", "Repositório local sem remote configurado.")
            except (subprocess.SubprocessError, OSError) as e:
                self._record("Git/GitHub", "Situação Git Online / Remoto", "WARN", f"Falha ao checar git remoto: {e}")
        else:
            self._record("Git/GitHub", "Situação Git Online / Remoto", "WARN", "Diretório .git não inicializado.")

    def _check_ci_cd(self) -> None:
        workflows_dir = self.project_path / ".github" / "workflows"
        if workflows_dir.is_dir():
            yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            if yaml_files:
                self._record("CI/CD", "Workflow de CI", "PASS", f"{len(yaml_files)} workflow(s) encontrado(s) em .github/workflows/.")
            else:
                self._record("CI/CD", "Workflow de CI", "FAIL", "Nenhum arquivo YAML de pipeline em .github/workflows/.")
        else:
            self._record("CI/CD", "Workflow de CI", "FAIL", "Diretório .github/workflows/ ausente.")

    def _check_security_and_config(self) -> None:
        # .env.example
        env_example = self.project_path / ".env.example"
        if env_example.is_file():
            self._record("Segurança/Config", ".env.example", "PASS", ".env.example presente.")
        else:
            self._record("Segurança/Config", ".env.example", "FAIL", ".env.example ausente.")

        # Leak check: .env no repo
        real_env = self.project_path / ".env"
        gitignore = self.project_path / ".gitignore"
        if real_env.exists():
            if gitignore.is_file():
                content = gitignore.read_text(encoding="utf-8", errors="ignore")
                if ".env" in content:
                    self._record("Segurança/Config", "Proteção de .env real", "PASS", ".env existe localmente mas está ignorado no .gitignore.")
                else:
                    self._record("Segurança/Config", "Proteção de .env real", "FAIL", "PERIGO: .env presente sem entrada correspondente no .gitignore!")
            else:
                self._record("Segurança/Config", "Proteção de .env real", "FAIL", "PERIGO: .env presente sem .gitignore!")

        # LICENSE
        license_candidates = [self.project_path / "LICENSE", self.project_path / "LICENSE.md", self.project_path / "LICENSE.txt"]
        if any(p.is_file() for p in license_candidates):
            self._record("Segurança/Config", "LICENSE", "PASS", "Arquivo LICENSE presente.")
        else:
            self._record("Segurança/Config", "LICENSE", "WARN", "Arquivo LICENSE não encontrado.")

    def _check_code_quality(self) -> None:
        # Checa configs de linter/formatter comuns
        has_linter = False
        linter_indicators = [
            ".eslintrc", ".eslintrc.json", ".eslintrc.js", "eslint.config.js", "eslint.config.mjs",
            "ruff.toml", ".flake8", ".golangci.yml", ".golangci.yaml", "tslint.json", "biome.json"
        ]
        if any((self.project_path / f).exists() for f in linter_indicators):
            has_linter = True
        
        # Checa se pyproject.toml ou package.json contém menção a linter
        pkg_json = self.project_path / "package.json"
        if pkg_json.is_file():
            content = pkg_json.read_text(encoding="utf-8", errors="ignore").lower()
            if any(k in content for k in ["eslint", "prettier", "biome", "lint"]):
                has_linter = True

        pyproject = self.project_path / "pyproject.toml"
        if pyproject.is_file():
            content = pyproject.read_text(encoding="utf-8", errors="ignore").lower()
            if any(k in content for k in ["ruff", "black", "flake8", "pylint"]):
                has_linter = True

        if has_linter:
            self._record("Qualidade de Código", "Linter / Formatter", "PASS", "Configuração de linter/formatter detectada.")
        else:
            self._record("Qualidade de Código", "Linter / Formatter", "WARN", "Configuração explícita de linter não identificada.")


def main() -> int:
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    parser = argparse.ArgumentParser(description="Validador de Baseline Mínimo Universal de Projetos")
    parser.add_argument("path", nargs="?", default=".", help="Caminho do projeto a inspecionar (padrão: .)")
    parser.add_argument("--json", action="store_true", help="Retorna o resultado formatado em JSON")
    args = parser.parse_args()

    project_dir = Path(args.path)
    verifier = BaselineVerifier(project_dir)
    res = verifier.verify_all()

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["passed"] else 1

    print("=" * 70)
    print(f"📦 AUDITORIA DE BASELINE MÍNIMO: {res.get('project_path')}")
    print("=" * 70)

    if "error" in res:
        print(f"❌ ERRO: {res['error']}")
        return 1

    current_cat = ""
    for r in res["results"]:
        if r["category"] != current_cat:
            current_cat = r["category"]
            print(f"\n[{current_cat}]")
        
        status_icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}.get(r["status"], "❓")
        print(f"  {status_icon} {r['item']}: {r['detail']}")

    print("\n" + "-" * 70)
    print(f"Conformidade Geral: {res['score']}% ({res['passed_checks']}/{res['total_checks']} checagens aprovadas)")
    if res["passed"]:
        print("🎉 STATUS: APROVADO no baseline mínimo obrigatório.")
        return 0
    else:
        print("⚠️ STATUS: REPROVADO. Existem itens mandatórios com status FAIL.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
