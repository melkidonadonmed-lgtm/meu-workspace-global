"""Harness de Teste Empírico e Estresse Adversarial — Milestone 1 (M1) Gen 2.

Executado pelo Challenger 1 para validar:
1. Resolução de todas as chaves e caminhos da SSoT projects.json.
2. Variações de casing (UPPERCASE, TitleCase, Snake_Case, Kebab-Case, etc.).
3. Normalização de barras (Windows vs POSIX vs Mixed vs Trailing).
4. Detecção profunda de stack em diretórios sintéticos (Node/React 19, Python, Go, Monorepo, Manifests vazios/corrompidos).
5. Robustez contra entradas inválidas, vazias e boundary conditions.
6. Integração com WorkspaceSpecialistAgent e projects_dashboard.py.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Garantir PYTHONPATH
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from pydantic import BaseModel

from agents.project_resolver import (
    CANONICAL_PROJECTS_JSON,
    KNOWN_METADATA,
    KNOWN_PROJECT_NAMES,
    ManifestInfo,
    ProjectTargetInfo,
    ProjectTargetResolver,
    StackDetails,
)
from agents.specialized.workspace_specialist import WorkspaceSpecialistAgent


class TestResult:
    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.passed = 0
        self.failed = 0
        self.errors: list[str] = []

    def assert_true(self, condition: bool, message: str):
        if condition:
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append(f"FAIL: {message}")
            print(f"  ❌ FAIL: {message}")

    def assert_equal(self, actual: Any, expected: Any, message: str):
        if actual == expected:
            self.passed += 1
        else:
            self.failed += 1
            err = f"FAIL: {message} | Esperado: {expected!r} | Obtido: {actual!r}"
            self.errors.append(err)
            print(f"  ❌ {err}")

    def report(self):
        status = "PASSED" if self.failed == 0 else "FAILED"
        print(f"\n[{status}] {self.suite_name}: {self.passed} pass, {self.failed} fail")
        for err in self.errors:
            print(f"    - {err}")
        return self.failed == 0


def run_oracle_1_ssot_completeness() -> bool:
    print("\n" + "=" * 70)
    print("ORACLE 1: Resolução Completa da SSoT (projects.json)")
    print("=" * 70)
    res = TestResult("Oracle 1 - SSoT Completeness")

    res.assert_true(CANONICAL_PROJECTS_JSON.exists(), f"projects.json canônico deve existir em {CANONICAL_PROJECTS_JSON}")
    if not CANONICAL_PROJECTS_JSON.exists():
        return False

    raw_data = json.loads(CANONICAL_PROJECTS_JSON.read_text(encoding="utf-8"))
    registered = raw_data.get("projects", {})

    all_projs = ProjectTargetResolver.list_all_projects(include_system=True)
    all_keys = {p.key for p in all_projs}

    for raw_path, slug in registered.items():
        norm_path = Path(raw_path).resolve()
        slug_clean = str(slug).strip()

        # 1. Deve estar na lista de projetos (include_system=True)
        res.assert_true(slug_clean in all_keys, f"Slug '{slug_clean}' deve estar em list_all_projects(include_system=True)")

        # 2. Resolução por slug direto via resolve_project
        info_slug = ProjectTargetResolver.resolve_project(slug_clean)
        res.assert_true(isinstance(info_slug, ProjectTargetInfo), f"resolve_project('{slug_clean}') deve retornar ProjectTargetInfo")
        res.assert_equal(info_slug.key, slug_clean, f"Key do projeto deve ser '{slug_clean}'")

        # 3. Resolução por get_project passando raw_path
        info_path = ProjectTargetResolver.get_project(raw_path)
        if norm_path.exists():
            res.assert_true(info_path is not None, f"get_project('{raw_path}') deve resolver caminho existente")
            if info_path:
                res.assert_equal(info_path.canonical_path.resolve(), norm_path, f"canonical_path deve bater com {norm_path}")

        # 4. Resolução por get_project passando Path(raw_path)
        info_path_obj = ProjectTargetResolver.get_project(Path(raw_path))
        if norm_path.exists():
            res.assert_true(info_path_obj is not None, f"get_project(Path('{raw_path}')) deve resolver caminho existente")

        # 5. Validação de exists
        if norm_path.exists():
            res.assert_true(info_slug.exists, f"info_slug.exists deve ser True para caminho existente {norm_path}")

    return res.report()


def run_oracle_2_casing_resilience() -> bool:
    print("\n" + "=" * 70)
    print("ORACLE 2: Resiliência a Variações de Casing")
    print("=" * 70)
    res = TestResult("Oracle 2 - Casing Resilience")

    casing_cases = [
        # (identificador_teste, chave_esperada)
        ("PCM", "pcm"),
        ("Pcm", "pcm"),
        ("pCm", "pcm"),
        ("PRESCMED", "pcm"),
        ("PrescMed", "pcm"),
        ("prescmed-pcm", "pcm"),
        ("PRESCMED-PCM", "pcm"),
        ("canvas_ide", "canvas-ide"),  # Nota: projects.json mapeia canvas_ide como slug canvas-ide
        ("CANVAS_IDE", "canvas-ide"),
        ("Canvas_Ide", "canvas-ide"),
        ("canvas-ide", "canvas-ide"),
        ("CANVAS-IDE", "canvas-ide"),
        ("Canvas-Ide", "canvas-ide"),
        ("canvas", "canvas-ide"),
        ("CANVAS", "canvas-ide"),
        ("waoe", "waoe"),
        ("WAOE", "waoe"),
        ("wAoE", "waoe"),
        ("Waoe", "waoe"),
        ("remix-prescmed-new", "remix-prescmed-new"),
        ("REMIX-PRESCMED-NEW", "remix-prescmed-new"),
        ("Remix-Prescmed-New", "remix-prescmed-new"),
        ("remix-prescmed", "remix-prescmed-new"),
        ("REMIX", "remix-prescmed-new"),
        ("tactile-ui-studio", "tactile-ui-studio"),
        ("TACTILE-UI-STUDIO", "tactile-ui-studio"),
        ("Tactile_Ui_Studio", "tactile-ui-studio"),
        ("tactile", "tactile-ui-studio"),
        ("TACTILE", "tactile-ui-studio"),
        ("atlas-ui-kit", "tactile-ui-studio"),
        ("ATLAS-UI-KIT", "tactile-ui-studio"),
        ("mdk-teste", "mdk-teste"),
        ("MDK-TESTE", "mdk-teste"),
        ("Mdk_Teste", "mdk-teste"),
        ("MDK", "mdk-teste"),
        ("customer_issue_reviewer_go", "customer_issue_reviewer_go"),
        ("CUSTOMER_ISSUE_REVIEWER_GO", "customer_issue_reviewer_go"),
        ("Customer_Issue_Reviewer_Go", "customer_issue_reviewer_go"),
        ("customer-issue-reviewer", "customer_issue_reviewer_go"),
        ("web_visual_auditor", "web_visual_auditor"),
        ("WEB_VISUAL_AUDITOR", "web_visual_auditor"),
        ("Web-Visual-Auditor", "web_visual_auditor"),
    ]

    for input_ident, expected_key in casing_cases:
        # Teste via get_project
        proj = ProjectTargetResolver.get_project(input_ident)
        res.assert_true(proj is not None, f"get_project('{input_ident}') não deve ser None")
        if proj:
            res.assert_equal(proj.key.lower(), expected_key.lower(), f"get_project('{input_ident}') key esperada: {expected_key}")

        # Teste via resolve_project
        info = ProjectTargetResolver.resolve_project(input_ident)
        res.assert_true(info.exists, f"resolve_project('{input_ident}') deve encontrar projeto existente (exists=True)")
        res.assert_equal(info.key.lower(), expected_key.lower(), f"resolve_project('{input_ident}') key esperada: {expected_key}")

    # Teste de linguagem natural com casing variado via resolve_target
    natural_queries = [
        ("audite a interface do projeto PCM para criancas", "pcm"),
        ("reorganize o layout no CANVAS_IDE", "canvas-ide"),
        ("verifique o orquestrador WAOE agora", "waoe"),
        ("abra o TACTILE-UI-STUDIO monorepo", "tactile-ui-studio"),
        ("execute os testes do REMIX-PRESCMED-NEW", "remix-prescmed-new"),
        ("diagnostique a pipeline MDK-TESTE", "mdk-teste"),
    ]

    for phrase, expected_key in natural_queries:
        target = ProjectTargetResolver.resolve_target(phrase, workspace_root=WORKSPACE_ROOT)
        res.assert_true(target is not None, f"resolve_target('{phrase}') não deve ser None")
        if target:
            res.assert_equal(target.key.lower(), expected_key.lower(), f"resolve_target('{phrase}') key esperada: {expected_key}")

    return res.report()


def run_oracle_3_path_normalization() -> bool:
    print("\n" + "=" * 70)
    print("ORACLE 3: Normalização de Barras e Variações de Caminho")
    print("=" * 70)
    res = TestResult("Oracle 3 - Path Normalization")

    path_variations = [
        (r"C:\Users\melki\Projetos\pcm", "pcm"),
        ("C:/Users/melki/Projetos/pcm", "pcm"),
        ("c:/users/melki/projetos/pcm", "pcm"),
        (r"c:\users\melki\projetos\pcm", "pcm"),
        ("C:/Users/melki/Projetos/pcm/", "pcm"),
        (r"C:\Users\melki\Projetos\pcm\\", "pcm"),
        (r"C:\Users\melki\Projetos/pcm", "pcm"),
        ("projects/pcm", "pcm"),
        (r"projects\pcm", "pcm"),
        ("projects/pcm/", "pcm"),
    ]

    for p_var, expected_key in path_variations:
        proj = ProjectTargetResolver.get_project(p_var, workspace_root=WORKSPACE_ROOT)
        res.assert_true(proj is not None, f"get_project('{p_var}') deve resolver caminho")
        if proj:
            res.assert_equal(proj.key.lower(), expected_key.lower(), f"Caminho '{p_var}' deve resolver para key '{expected_key}'")
            res.assert_true(proj.canonical_path.is_absolute(), f"canonical_path deve ser absoluto para '{p_var}'")

    # Teste de junction path em projects/
    junction_dir = WORKSPACE_ROOT / "projects" / "pcm"
    if junction_dir.exists():
        proj_junc = ProjectTargetResolver.get_project(junction_dir, workspace_root=WORKSPACE_ROOT)
        res.assert_true(proj_junc is not None, "get_project para junction_dir não deve ser None")
        if proj_junc:
            res.assert_equal(proj_junc.key, "pcm", "junction deve resolver para pcm")
            res.assert_true(proj_junc.is_junction, "is_junction deve ser True para junction em projects/")

    return res.report()


def run_oracle_4_synthetic_stack_detection() -> bool:
    print("\n" + "=" * 70)
    print("ORACLE 4: Detecção Profunda de Stack (Diretórios Sintéticos & Monorepo)")
    print("=" * 70)
    res = TestResult("Oracle 4 - Synthetic Stack Detection")

    with tempfile.TemporaryDirectory() as tmpdir:
        base_tmp = Path(tmpdir)

        # 4.1. Sintético React 19 + Vite + Tailwind + Express + Firebase + Google GenAI
        p1 = base_tmp / "react_advanced"
        p1.mkdir()
        (p1 / "package.json").write_text(
            json.dumps({
                "name": "my-react-app",
                "version": "1.0.0",
                "scripts": {"dev": "vite --port 3333", "build": "vite build"},
                "dependencies": {
                    "react": "^19.0.0",
                    "react-dom": "^19.0.0",
                    "express": "^4.21.0",
                    "firebase": "^10.0.0",
                    "@google/genai": "^0.1.0",
                    "@xyflow/react": "^12.0.0",
                },
                "devDependencies": {
                    "typescript": "^5.6.0",
                    "vite": "^6.0.0",
                    "tailwindcss": "^4.0.0",
                    "@tailwindcss/vite": "^4.0.0",
                },
            }),
            encoding="utf-8",
        )
        (p1 / "tsconfig.json").write_text("{}", encoding="utf-8")
        (p1 / "bun.lock").write_text("", encoding="utf-8")

        stack1 = ProjectTargetResolver.detect_stack(p1)
        res.assert_equal(stack1.primary_language, "TypeScript", "P1 primary_language deve ser TypeScript")
        res.assert_equal(stack1.package_manager, "bun", "P1 package_manager deve ser bun")
        res.assert_equal(stack1.default_port, 3333, "P1 default_port deve ser 3333")
        res.assert_true("React 19" in stack1.frameworks, "P1 deve conter React 19")
        res.assert_true("Vite" in stack1.frameworks, "P1 deve conter Vite")
        res.assert_true("Tailwind CSS" in stack1.frameworks, "P1 deve conter Tailwind CSS")
        res.assert_true("Express" in stack1.frameworks, "P1 deve conter Express")
        res.assert_true("Firebase" in stack1.frameworks, "P1 deve conter Firebase")
        res.assert_true("Google GenAI" in stack1.frameworks, "P1 deve conter Google GenAI")
        res.assert_true("XYFlow" in stack1.frameworks, "P1 deve conter XYFlow")
        res.assert_equal(stack1.package_name, "my-react-app", "P1 package_name deve bater")

        # 4.2. Sintético Python (pyproject.toml) com FastAPI, Pydantic, Pytest, Playwright
        p2 = base_tmp / "py_advanced"
        p2.mkdir()
        (p2 / "pyproject.toml").write_text(
            """
[project]
name = "my-fastapi-service"
version = "0.2.0"
dependencies = [
    "fastapi>=0.115.0",
    "pydantic>=2.10.0",
    "httpx>=0.27.0",
    "rich>=13.8.0",
    "pyspark>=3.5.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "playwright>=1.47.0"
]
""",
            encoding="utf-8",
        )
        (p2 / "uv.lock").write_text("", encoding="utf-8")

        stack2 = ProjectTargetResolver.detect_stack(p2)
        res.assert_equal(stack2.primary_language, "Python", "P2 primary_language deve ser Python")
        res.assert_equal(stack2.package_manager, "uv", "P2 package_manager deve ser uv")
        res.assert_equal(stack2.dev_command, "uv run pytest", "P2 dev_command deve ser 'uv run pytest'")
        res.assert_true("FastAPI" in stack2.frameworks, "P2 deve conter FastAPI")
        res.assert_true("Pydantic" in stack2.frameworks, "P2 deve conter Pydantic")
        res.assert_true("Pytest" in stack2.frameworks, "P2 deve conter Pytest")
        res.assert_true("Playwright" in stack2.frameworks, "P2 deve conter Playwright")
        res.assert_true("HTTPX" in stack2.frameworks, "P2 deve conter HTTPX")
        res.assert_true("Rich" in stack2.frameworks, "P2 deve conter Rich")
        res.assert_true("PySpark" in stack2.frameworks, "P2 deve conter PySpark")

        # 4.3. Sintético Python (requirements.txt)
        p3 = base_tmp / "py_reqs"
        p3.mkdir()
        (p3 / "requirements.txt").write_text(
            """
# Core web
flask>=3.0.0
beautifulsoup4==4.12.3
streamlit>=1.38.0
""",
            encoding="utf-8",
        )
        stack3 = ProjectTargetResolver.detect_stack(p3)
        res.assert_equal(stack3.primary_language, "Python", "P3 primary_language deve ser Python")
        res.assert_true("Flask" in stack3.frameworks, "P3 deve conter Flask")
        res.assert_true("BeautifulSoup4" in stack3.frameworks, "P3 deve conter BeautifulSoup4")
        res.assert_true("Streamlit" in stack3.frameworks, "P3 deve conter Streamlit")

        # 4.4. Sintético Go (go.mod) com Google ADK, Google GenAI, Gin
        p4 = base_tmp / "go_advanced"
        p4.mkdir()
        (p4 / "go.mod").write_text(
            """
module github.com/user/my-go-agent

go 1.23.0

require (
    google.golang.org/adk v0.1.0
    google.golang.org/genai v0.2.0
    github.com/gin-gonic/gin v1.10.0
)
""",
            encoding="utf-8",
        )
        stack4 = ProjectTargetResolver.detect_stack(p4)
        res.assert_equal(stack4.primary_language, "Go", "P4 primary_language deve ser Go")
        res.assert_equal(stack4.package_manager, "go", "P4 package_manager deve ser go")
        res.assert_equal(stack4.package_name, "github.com/user/my-go-agent", "P4 package_name correto")
        res.assert_true("Google ADK" in stack4.frameworks, "P4 deve conter Google ADK")
        res.assert_true("Google GenAI" in stack4.frameworks, "P4 deve conter Google GenAI")
        res.assert_true("Gin" in stack4.frameworks, "P4 deve conter Gin")

        # 4.5. Sintético Monorepo (manifest em apps/atlas-ui-kit/)
        p5 = base_tmp / "monorepo_tactile"
        p5.mkdir()
        sub_app = p5 / "apps" / "atlas-ui-kit"
        sub_app.mkdir(parents=True)
        (sub_app / "package.json").write_text(
            json.dumps({
                "name": "@tactile/atlas-ui-kit",
                "scripts": {"dev": "vite"},
                "dependencies": {"react": "^19.0.0", "tailwindcss": "^4.0.0"},
                "devDependencies": {"vite": "^6.0.0"},
            }),
            encoding="utf-8",
        )
        stack5 = ProjectTargetResolver.detect_stack(p5)
        res.assert_true("React 19" in stack5.frameworks, "P5 monorepo deve detectar React 19 em apps/atlas-ui-kit")
        res.assert_true("Vite" in stack5.frameworks, "P5 monorepo deve detectar Vite")
        res.assert_equal(stack5.package_name, "@tactile/atlas-ui-kit", "P5 package_name deve ser extraído de subpasta")

        # 4.6. Manifest JSON vazio {}
        p6 = base_tmp / "empty_json"
        p6.mkdir()
        (p6 / "package.json").write_text("{}", encoding="utf-8")
        stack6 = ProjectTargetResolver.detect_stack(p6)
        res.assert_equal(stack6.manifest_type, "package.json", "P6 deve registrar manifest_type package.json")
        res.assert_equal(stack6.frameworks, [], "P6 não deve ter frameworks")

        # 4.7. Manifest JSON malformado (syntax error)
        p7 = base_tmp / "corrupt_json"
        p7.mkdir()
        (p7 / "package.json").write_text("{corrompido: true", encoding="utf-8")
        stack7 = ProjectTargetResolver.detect_stack(p7)
        res.assert_equal(stack7.manifest_type, "package.json", "P7 deve lidar graciosamente com JSON corrompido")
        res.assert_equal(stack7.frameworks, [], "P7 não deve quebrar com crash")

        # 4.8. TOML malformado
        p8 = base_tmp / "corrupt_toml"
        p8.mkdir()
        (p8 / "pyproject.toml").write_text("[[[bad toml]]", encoding="utf-8")
        stack8 = ProjectTargetResolver.detect_stack(p8)
        res.assert_equal(stack8.primary_language, "Python", "P8 deve identificar Python sem crashar")

        # 4.9. Diretório inexistente
        p9 = base_tmp / "non_existent_999"
        stack9 = ProjectTargetResolver.detect_stack(p9)
        res.assert_equal(stack9.primary_language, "Unknown", "P9 inexistente deve retornar Unknown")
        res.assert_equal(stack9.frameworks, [], "P9 frameworks deve ser vazio")

    return res.report()


def run_oracle_5_edge_cases_and_contracts() -> bool:
    print("\n" + "=" * 70)
    print("ORACLE 5: Edge Cases, Boundary Conditions e Contratos Tipados")
    print("=" * 70)
    res = TestResult("Oracle 5 - Edge Cases & Contracts")

    # 1. Identificador vazio ou apenas espaços
    info_empty = ProjectTargetResolver.resolve_project("")
    res.assert_true(isinstance(info_empty, ProjectTargetInfo), "resolve_project('') deve retornar ProjectTargetInfo")
    res.assert_equal(info_empty.exists, False, "resolve_project('') exists deve ser False")

    info_spaces = ProjectTargetResolver.resolve_project("     ")
    res.assert_true(isinstance(info_spaces, ProjectTargetInfo), "resolve_project('   ') deve retornar ProjectTargetInfo")
    res.assert_equal(info_spaces.exists, False, "resolve_project('   ') exists deve ser False")

    # 2. Injeção de caminho relativo para diretório inexistente
    info_path_inj = ProjectTargetResolver.resolve_project("../../fantasma/inexistente")
    res.assert_true(isinstance(info_path_inj, ProjectTargetInfo), "Injeção de caminho deve retornar ProjectTargetInfo")
    res.assert_equal(info_path_inj.exists, False, "Injeção de caminho deve ter exists=False")

    # 3. Serialização to_dict() e model_dump()
    pcm = ProjectTargetResolver.resolve_project("pcm")
    res.assert_true(isinstance(pcm, BaseModel), "pcm deve ser instância de Pydantic BaseModel")
    pcm_dict = pcm.to_dict()
    res.assert_true(isinstance(pcm_dict, dict), "to_dict() deve retornar dict")
    res.assert_equal(pcm_dict["key"], "pcm", "dict key deve ser pcm")
    res.assert_true("stack" in pcm_dict, "dict deve conter 'stack'")
    res.assert_true(isinstance(pcm_dict["stack"], dict), "'stack' serializado deve ser dict")
    res.assert_equal(pcm.model_dump()["key"], "pcm", "model_dump() deve funcionar")

    # 4. scan_directory em pasta inexistente
    scan_fake = ProjectTargetResolver.scan_directory(Path(r"C:\Users\melki\caminho_inexistente_12345"))
    res.assert_equal(scan_fake["status"], "success", "scan_directory deve retornar status success mesmo para pasta vazia")
    res.assert_equal(scan_fake["total_items_scanned"], 0, "total_items_scanned deve ser 0")

    return res.report()


def run_oracle_6_integration_and_dashboard() -> bool:
    print("\n" + "=" * 70)
    print("ORACLE 6: Integração com WorkspaceSpecialist e Projects Dashboard")
    print("=" * 70)
    res = TestResult("Oracle 6 - Integration & Dashboard")

    # 1. WorkspaceSpecialistAgent
    specialist = WorkspaceSpecialistAgent(str(WORKSPACE_ROOT))
    scan_res = specialist.scan_workspace("projects/pcm", max_depth=2)
    res.assert_equal(scan_res["agent"], "WorkspaceSpecialistAgent", "WorkspaceSpecialistAgent deve assumir autoria da resposta")
    res.assert_true(scan_res["is_target_project"], "is_target_project deve ser True")
    res.assert_true("React" in scan_res.get("tech_stack", []), "tech_stack deve conter React")

    # 2. projects_dashboard.py
    dashboard_path = Path(r"C:\Users\melki\.gemini\scripts\projects_dashboard.py")
    res.assert_true(dashboard_path.exists(), "projects_dashboard.py deve existir")

    # Importar e testar scan_all_projects()
    sys.path.insert(0, str(dashboard_path.parent))
    import projects_dashboard

    dashboard_projects = projects_dashboard.scan_all_projects()
    res.assert_true(len(dashboard_projects) >= 6, f"scan_all_projects() deve retornar pelo menos 6 projetos (obtido: {len(dashboard_projects)})")

    keys_dash = {p["key"] for p in dashboard_projects}
    res.assert_true("pcm" in keys_dash, "pcm deve estar no dashboard")
    res.assert_true("canvas-ide" in keys_dash or "canvas_ide" in keys_dash, "canvas deve estar no dashboard")
    res.assert_true("waoe" in keys_dash or "WAOE" in keys_dash, "waoe deve estar no dashboard")
    res.assert_true("remix-prescmed-new" in keys_dash, "remix-prescmed-new deve estar no dashboard")
    res.assert_true("tactile-ui-studio" in keys_dash, "tactile-ui-studio deve estar no dashboard")

    return res.report()


def main():
    print("=" * 70)
    print("INICIANDO SUÍTE EMPÍRICA ADVERSARIAL — CHALLENGER 1 (M1 GEN 2)")
    print("=" * 70)

    results = [
        run_oracle_1_ssot_completeness(),
        run_oracle_2_casing_resilience(),
        run_oracle_3_path_normalization(),
        run_oracle_4_synthetic_stack_detection(),
        run_oracle_5_edge_cases_and_contracts(),
        run_oracle_6_integration_and_dashboard(),
    ]

    all_passed = all(results)
    print("\n" + "=" * 70)
    print(f"VEREDICTO FINAL DO HARNESS EMPÍRICO: {'APROVADO (ALL PASS)' if all_passed else 'REPROVADO (FAILURES DETECTED)'}")
    print("=" * 70)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
