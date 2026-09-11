"""Tier 1: Feature Coverage (Casos de Uso Feliz Isolados por Feature).

Cobre exaustivamente as Features 1 a 14 listadas no Feature Inventory do PROJECT.md,
com no mínimo 5 testes por feature cobrindo cada comportamento esperado.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from agents.project_resolver import ProjectTargetResolver
from agents.specialized.workspace_specialist import WorkspaceSpecialistAgent
from tests.e2e.conftest import (
    CANONICAL_HOOK_SCRIPT,
    CANONICAL_PROJECTS_DIR,
    CANONICAL_PROJECTS_JSON,
    DASHBOARD_SCRIPT,
    HEALTHCHECK_SCRIPT,
    HUB_GEMINI_DIR,
    WORKSPACE_HOOK_SCRIPT,
    WORKSPACE_ROOT,
    run_hook_subprocess,
)


# ============================================================================
# Feature 1: SSoT Canonical Projects Registry (projects.json)
# ============================================================================

class TestFeature01ProjectsRegistrySSoT:
    """Valida a SSoT canônica de projetos em C:\\Users\\melki\\.gemini\\projects.json."""

    def test_f1_canonical_projects_json_exists_and_valid(self):
        assert CANONICAL_PROJECTS_JSON.exists(), "Arquivo canônico projects.json não encontrado!"
        data = json.loads(CANONICAL_PROJECTS_JSON.read_text(encoding="utf-8"))
        assert "projects" in data, "Chave 'projects' ausente no projects.json"
        assert isinstance(data["projects"], dict)

    def test_f1_canonical_projects_json_contains_core_client_projects(self):
        data = json.loads(CANONICAL_PROJECTS_JSON.read_text(encoding="utf-8"))
        projects = data["projects"]
        values = list(projects.values())
        for expected in ["pcm", "canvas-ide", "waoe", "keepdocs-workspace", "remix-prescmed-new"]:
            assert expected in values, f"Projeto esperado '{expected}' ausente no projects.json"

    def test_f1_canonical_projects_json_structure_and_path_keys(self):
        data = json.loads(CANONICAL_PROJECTS_JSON.read_text(encoding="utf-8"))
        projects = data["projects"]
        assert len(projects) >= 10, "projects.json deve conter pelo menos 10 mapeamentos"
        for path_key, identifier in projects.items():
            assert isinstance(path_key, str)
            assert len(path_key) > 0
            assert isinstance(identifier, str)
            assert len(identifier) > 0

    def test_f1_canonical_projects_json_workspace_and_hub_binding(self):
        data = json.loads(CANONICAL_PROJECTS_JSON.read_text(encoding="utf-8"))
        projects = data["projects"]
        values = list(projects.values())
        assert "meu-workspace-global" in values
        assert "melki" in values or "projetos" in values

    def test_f1_canonical_projects_json_path_resolution(self):
        data = json.loads(CANONICAL_PROJECTS_JSON.read_text(encoding="utf-8"))
        for path_str in data["projects"].keys():
            p = Path(path_str)
            # Todos os caminhos devem ser absolutos ou resolvíveis
            assert p.is_absolute(), f"Caminho no projects.json não é absoluto: {path_str}"


# ============================================================================
# Feature 2: Deep Project Target Resolver
# ============================================================================

class TestFeature02ProjectTargetResolver:
    """Valida a resolução determinística de projetos clientes via ProjectTargetResolver."""

    def test_f2_resolve_target_pcm_alias(self):
        resolver = ProjectTargetResolver()
        info = resolver.resolve_target("audite a interface do prescmed", WORKSPACE_ROOT)
        assert info is not None
        assert info.name == "pcm"
        assert info.exists is True
        assert "pcm" in info.target_path.as_posix().lower()

    def test_f2_resolve_target_canvas_ide_alias(self):
        resolver = ProjectTargetResolver()
        info = resolver.resolve_target("reorganize o layout no canvas", WORKSPACE_ROOT)
        assert info is not None
        assert info.name == "canvas_ide"
        assert info.exists is True

    def test_f2_resolve_target_keepdocs_alias(self):
        resolver = ProjectTargetResolver()
        info = resolver.resolve_target("atualize a documentacao do keepdocs", WORKSPACE_ROOT)
        assert info is not None
        assert info.name == "keepdocs-workspace"
        assert info.exists is True

    def test_f2_resolve_target_waoe_alias(self):
        resolver = ProjectTargetResolver()
        info = resolver.resolve_target("execute testes no waoe", WORKSPACE_ROOT)
        assert info is not None
        assert info.name.lower() in ("waoe", "waoe orchestrator")

    def test_f2_resolve_target_returns_none_for_generic_query(self):
        resolver = ProjectTargetResolver()
        info = resolver.resolve_target("como está o clima hoje?", WORKSPACE_ROOT)
        assert info is None


# ============================================================================
# Feature 3: Unified Deep Stack Detection
# ============================================================================

class TestFeature03UnifiedDeepStackDetection:
    """Valida a detecção profunda de stacks tecnológicas a partir de manifestos."""

    def test_f3_detect_stack_node_react_vite(self, sample_node_manifest: Path):
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(sample_node_manifest)
        assert "Node.js/npm" in stack
        assert "React" in stack
        assert "Vite" in stack
        assert "TypeScript" in stack
        assert "Tailwind CSS" in stack

    def test_f3_detect_stack_python_pyproject(self, sample_python_manifest: Path):
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(sample_python_manifest)
        assert "Python" in stack

    def test_f3_detect_stack_go_mod(self, sample_go_manifest: Path):
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(sample_go_manifest)
        assert "Go" in stack

    def test_f3_detect_stack_real_pcm_project(self):
        pcm_dir = CANONICAL_PROJECTS_DIR / "pcm"
        if not pcm_dir.exists():
            pytest.skip("Diretório C:/Users/melki/Projetos/pcm não encontrado no ambiente")
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(pcm_dir)
        assert "Node.js/npm" in stack
        assert "React" in stack
        assert "Vite" in stack

    def test_f3_detect_stack_empty_directory(self, tmp_path: Path):
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(tmp_path)
        assert stack == []


# ============================================================================
# Feature 4: Elimination of Stack Detection Duplication
# ============================================================================

class TestFeature04EliminationOfStackDetectionDuplication:
    """Valida que WorkspaceSpecialistAgent atua em harmonia com o ProjectTargetResolver."""

    def test_f4_workspace_specialist_scan_workspace_structure(self):
        agent = WorkspaceSpecialistAgent(root_dir=str(WORKSPACE_ROOT))
        result = agent.scan_workspace(max_depth=1)
        assert result["agent"] == "WorkspaceSpecialistAgent"
        assert result["status"] == "success"
        assert "root_path" in result
        assert "tech_stack" in result
        assert "files" in result
        assert isinstance(result["files"], list)

    def test_f4_workspace_specialist_target_project_flag(self):
        agent = WorkspaceSpecialistAgent(root_dir=str(WORKSPACE_ROOT))
        # Escaneamento da própria raiz
        res_root = agent.scan_workspace(target_path=None, max_depth=1)
        assert res_root["is_target_project"] is False

        # Escaneamento de subprojeto/alvo
        pcm_dir = CANONICAL_PROJECTS_DIR / "pcm"
        if pcm_dir.exists():
            res_target = agent.scan_workspace(target_path=str(pcm_dir), max_depth=1)
            assert res_target["is_target_project"] is True

    @pytest.mark.xfail(
        condition=True,
        reason="Feature 4 (Delegação de stack detection em workspace_specialist.py) em implementação pelo Worker M1",
        strict=False,
    )
    def test_f4_workspace_specialist_tech_stack_matches_resolver(self, sample_node_manifest: Path):
        agent = WorkspaceSpecialistAgent(root_dir=str(WORKSPACE_ROOT))
        res = agent.scan_workspace(target_path=str(sample_node_manifest), max_depth=1)
        resolver = ProjectTargetResolver()
        resolver_stack = resolver._detect_tech_stack(sample_node_manifest)
        assert set(res["tech_stack"]) == set(resolver_stack)

    def test_f4_workspace_specialist_max_depth_filtering(self):
        agent = WorkspaceSpecialistAgent(root_dir=str(WORKSPACE_ROOT))
        res_depth1 = agent.scan_workspace(max_depth=1)
        res_depth2 = agent.scan_workspace(max_depth=2)
        assert res_depth1["total_items_scanned"] <= res_depth2["total_items_scanned"]

    def test_f4_workspace_specialist_skips_ignored_dirs(self):
        agent = WorkspaceSpecialistAgent(root_dir=str(WORKSPACE_ROOT))
        result = agent.scan_workspace(max_depth=3)
        files = result["files"]
        for f in files:
            assert ".venv" not in f
            assert "node_modules" not in f
            assert "__pycache__" not in f


# ============================================================================
# Feature 5: Projects Dashboard Integration (projects_dashboard.py)
# ============================================================================

class TestFeature05ProjectsDashboardIntegration:
    """Valida o painel unificado de projetos em C:\\Users\\melki\\.gemini\\scripts\\projects_dashboard.py."""

    def test_f5_dashboard_script_exists(self):
        assert DASHBOARD_SCRIPT.exists(), "Script projects_dashboard.py não encontrado!"

    def test_f5_dashboard_cli_json_execution(self):
        proc = subprocess.run(
            [sys.executable, str(DASHBOARD_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0, f"Dashboard falhou: {proc.stderr}"
        data = json.loads(proc.stdout)
        assert "projects" in data
        assert isinstance(data["projects"], list)
        assert len(data["projects"]) > 0

    def test_f5_dashboard_reports_pcm_metadata(self):
        proc = subprocess.run(
            [sys.executable, str(DASHBOARD_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        data = json.loads(proc.stdout)
        pcm_entry = next((p for p in data["projects"] if p["key"] == "pcm"), None)
        assert pcm_entry is not None, "Projeto 'pcm' não reportado no dashboard"
        assert pcm_entry["port"] == 3000
        assert "dev_cmd" in pcm_entry
        assert "git" in pcm_entry

    def test_f5_dashboard_port_check_functionality(self):
        # Valida que inspect_project relata status de porta sem lançar exceção
        proc = subprocess.run(
            [sys.executable, str(DASHBOARD_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        data = json.loads(proc.stdout)
        for p in data["projects"]:
            if p.get("exists"):
                assert "port_status" in p
                assert p["port_status"] in ("LIVRE", "ONLINE (Em execução)")

    def test_f5_dashboard_table_output_without_json(self):
        proc = subprocess.run(
            [sys.executable, str(DASHBOARD_SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "PAINEL CENTRAL DE SAÚDE DOS PROJETOS" in proc.stdout


# ============================================================================
# Feature 6: Directory Boundary Enforcement (pre_tool_guard.py)
# ============================================================================

class TestFeature06DirectoryBoundaryEnforcement:
    """Valida a interceptação de escritas fora do escopo de projetos autorizados."""

    def test_f6_allow_write_inside_authorized_projetos(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/Projetos/pcm/src/components/Header.tsx"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "allow"

    def test_f6_allow_write_inside_meu_workspace_global(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/meu-workspace-global/tests/e2e/test_sample.py"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "allow"

    def test_f6_allow_write_inside_subagent_dedicated_folder(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/.agents/e2e_test_writer_1/handoff.md"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "allow"

    @pytest.mark.xfail(
        condition=True,
        reason="Feature 6 (Directory Boundary Enforcement) pendente de implementação no Milestone 2 conforme PROJECT.md",
        strict=False,
    )
    def test_f6_intercept_write_to_windows_system(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Windows/System32/drivers/etc/hosts"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") in ("force_ask", "deny")

    @pytest.mark.xfail(
        condition=True,
        reason="Feature 6 (Directory Boundary Enforcement) pendente de implementação no Milestone 2 conforme PROJECT.md",
        strict=False,
    )
    def test_f6_intercept_write_to_user_home_root(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/malicious_startup.bat"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") in ("force_ask", "deny")


# ============================================================================
# Feature 7: Sensitive Files Mutation Interception
# ============================================================================

class TestFeature07SensitiveFilesMutationInterception:
    """Valida interceptação de mutações em arquivos sensíveis com HITL (force_ask)."""

    def test_f7_intercept_env_file_mutation(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/Projetos/pcm/.env"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"
        assert "Zero-Trust" in res.get("reason", "")

    def test_f7_intercept_credentials_json_mutation(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/meu-workspace-global/configs/credentials.json"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f7_intercept_id_rsa_mutation(self):
        payload = {
            "toolCall": {
                "name": "replace_file_content",
                "args": {"TargetFile": "C:/Users/melki/.ssh/id_rsa"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f7_intercept_service_account_mutation(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/gcp/service_account.json"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f7_allow_normal_code_file_mutation(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/Projetos/pcm/src/App.tsx"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "allow"


# ============================================================================
# Feature 8: High-Risk Destructive Commands Interception
# ============================================================================

class TestFeature08HighRiskDestructiveCommandsInterception:
    """Valida a interceptação de comandos de alto risco disparando force_ask."""

    def test_f8_intercept_rm_rf(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "rm -rf /"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f8_intercept_remove_item_recurse(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "Remove-Item -Path C:/Projetos -Recurse"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f8_intercept_git_reset_hard(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "git reset --hard origin/main"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f8_intercept_git_push_force(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "git push origin main --force"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f8_allow_safe_commands(self):
        for cmd in ["git status", "npm run dev", "uv run pytest", "dir", "echo 'hello'"]:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd},
                }
            }
            res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
            assert res.get("decision") == "allow", f"Comando seguro falhou: {cmd}"


# ============================================================================
# Feature 9: Seam Canonical Synchronization
# ============================================================================

class TestFeature09SeamCanonicalSynchronization:
    """Valida que o hook canônico em .gemini e o espelho no workspace operam com paridade estrita."""

    def test_f9_both_hook_files_exist(self):
        assert CANONICAL_HOOK_SCRIPT.exists(), "Hook canônico .gemini ausente!"
        assert WORKSPACE_HOOK_SCRIPT.exists(), "Hook espelho no workspace ausente!"

    def test_f9_both_hooks_valid_python_syntax(self):
        compile(CANONICAL_HOOK_SCRIPT.read_text(encoding="utf-8"), str(CANONICAL_HOOK_SCRIPT), "exec")
        compile(WORKSPACE_HOOK_SCRIPT.read_text(encoding="utf-8"), str(WORKSPACE_HOOK_SCRIPT), "exec")

    def test_f9_destructive_commands_parity(self):
        cmd = "rm -rf node_modules"
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": cmd}}}
        res_canon = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        res_work = run_hook_subprocess(WORKSPACE_HOOK_SCRIPT, payload)
        assert res_canon.get("decision") == res_work.get("decision") == "force_ask"

    def test_f9_sensitive_files_parity(self):
        target = "C:/Users/melki/Projetos/pcm/.env"
        payload = {"toolCall": {"name": "write_to_file", "args": {"TargetFile": target}}}
        res_canon = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        res_work = run_hook_subprocess(WORKSPACE_HOOK_SCRIPT, payload)
        assert res_canon.get("decision") == res_work.get("decision") == "force_ask"

    def test_f9_safe_payloads_parity(self):
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "git log -n 1"}}}
        res_canon = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        res_work = run_hook_subprocess(WORKSPACE_HOOK_SCRIPT, payload)
        assert res_canon.get("decision") == res_work.get("decision") == "allow"


# ============================================================================
# Feature 10: Ubiquitous Language Domain Model Sync (CONTEXT.md)
# ============================================================================

class TestFeature10UbiquitousLanguageDomainModelSync:
    """Valida a sincronização da linguagem ubíqua em CONTEXT.md."""

    def test_f10_context_md_exists_and_readable(self):
        ctx = WORKSPACE_ROOT / "CONTEXT.md"
        assert ctx.exists(), "CONTEXT.md não encontrado no workspace!"
        content = ctx.read_text(encoding="utf-8")
        assert len(content) > 200

    def test_f10_context_md_defines_core_ubiquitous_terms(self):
        content = (WORKSPACE_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        assert "**Meta-Workspace**" in content
        assert "**Projeto Alvo (Target Project)**" in content
        assert "**Skill**" in content
        assert "**Guardrail Zero-Trust**" in content

    def test_f10_context_md_contains_avoid_guidelines(self):
        content = (WORKSPACE_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        assert "_Avoid_:" in content

    @pytest.mark.xfail(
        condition=True,
        reason="Feature 10 (Expurgar Gateway SSE em CONTEXT.md) pendente de implementação no Milestone 3 conforme PROJECT.md",
        strict=False,
    )
    def test_f10_context_md_purged_deprecated_gateway_sse(self):
        content = (WORKSPACE_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        assert "Gateway SSE" not in content, "Termo obsoleto 'Gateway SSE' ainda presente em CONTEXT.md!"
        assert "porta 8000" not in content
        assert "porta 8080" not in content

    @pytest.mark.xfail(
        condition=True,
        reason="Feature 10 (Expurgar MasterOrchestrator em CONTEXT.md) pendente de implementação no Milestone 3 conforme PROJECT.md",
        strict=False,
    )
    def test_f10_context_md_purged_deprecated_master_orchestrator(self):
        content = (WORKSPACE_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        assert "MasterOrchestrator" not in content, "Termo obsoleto 'MasterOrchestrator' ainda presente em CONTEXT.md!"


# ============================================================================
# Feature 11: Architecture Decision Records Sync (docs/adr/)
# ============================================================================

class TestFeature11ArchitectureDecisionRecordsSync:
    """Valida integridade e sincronização dos registros arquiteturais em docs/adr/."""

    def test_f11_adr_directory_exists(self):
        adr_dir = WORKSPACE_ROOT / "docs" / "adr"
        assert adr_dir.exists(), "Diretório docs/adr/ não encontrado!"
        adrs = list(adr_dir.glob("*.md"))
        assert len(adrs) >= 4, "Devem existir pelo menos 4 ADRs registradas"

    def test_f11_adr_0001_meta_workspace_engine(self):
        adr = WORKSPACE_ROOT / "docs" / "adr" / "0001-meta-workspace-engine-architecture.md"
        assert adr.exists()
        content = adr.read_text(encoding="utf-8")
        assert "0001" in content or "ADR 0001" in content or "Meta-Workspace" in content

    def test_f11_adr_0002_target_project_binding(self):
        adr = WORKSPACE_ROOT / "docs" / "adr" / "0002-target-project-binding-and-hybrid-memory.md"
        assert adr.exists()
        content = adr.read_text(encoding="utf-8")
        assert "0002" in content or "ADR 0002" in content

    def test_f11_adr_0003_superseded_status(self):
        adr = WORKSPACE_ROOT / "docs" / "adr" / "0003-coordination-topology-and-resilience.md"
        assert adr.exists()
        content = adr.read_text(encoding="utf-8")
        assert "Superseded" in content or "Substituído" in content

    @pytest.mark.xfail(
        condition=True,
        reason="Feature 11 (Formalização do ADR 0005) pendente de criação no Milestone 3 conforme PROJECT.md",
        strict=False,
    )
    def test_f11_adr_0005_lifecycle_hooks_unification(self):
        adr = WORKSPACE_ROOT / "docs" / "adr" / "0005-antigravity-lifecycle-hooks-and-central-hub-unification.md"
        assert adr.exists(), "ADR 0005 sobre Lifecycle Hooks ainda não lavrada em docs/adr/"


# ============================================================================
# Feature 12: Pytest Teardown Windows Fix (pyproject.toml)
# ============================================================================

class TestFeature12PytestTeardownWindowsFix:
    """Valida que a configuração do pytest em pyproject.toml mitiga o WinError 5 no Windows."""

    def test_f12_pyproject_toml_exists(self):
        pyproj = WORKSPACE_ROOT / "pyproject.toml"
        assert pyproj.exists()

    def test_f12_tmp_path_retention_configured(self):
        content = (WORKSPACE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "tmp_path_retention_count" in content
        assert "tmp_path_retention_count = 0" in content

    def test_f12_basetemp_option_configured(self):
        content = (WORKSPACE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "--basetemp=" in content

    def test_f12_basetemp_target_directory_writable(self):
        target_temp = Path(r"C:\Users\melki\.pytest_temp")
        target_temp.mkdir(parents=True, exist_ok=True)
        test_file = target_temp / "write_probe.tmp"
        test_file.write_text("probe", encoding="utf-8")
        assert test_file.read_text(encoding="utf-8") == "probe"
        test_file.unlink()

    def test_f12_clean_session_execution(self):
        # Executa comando de teste rápido para validar teardown sem WinError 5
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/unit/test_project_resolver.py", "-q"],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "WinError 5" not in proc.stderr
        assert "PermissionError" not in proc.stderr


# ============================================================================
# Feature 13: Ecosystem Healthcheck Contracts Verification (ecosystem_healthcheck.py)
# ============================================================================

class TestFeature13EcosystemHealthcheckContractsVerification:
    """Valida o verificador de conformidade do Hub Central (ecosystem_healthcheck.py)."""

    def test_f13_healthcheck_script_exists(self):
        assert HEALTHCHECK_SCRIPT.exists(), "Script ecosystem_healthcheck.py ausente no Hub!"

    def test_f13_healthcheck_cli_json_execution(self):
        proc = subprocess.run(
            [sys.executable, str(HEALTHCHECK_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert "is_healthy" in data
        assert "total_checks" in data
        assert "passed_checks" in data
        assert "items" in data

    def test_f13_healthcheck_evaluates_json_configs(self):
        proc = subprocess.run(
            [sys.executable, str(HEALTHCHECK_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        data = json.loads(proc.stdout)
        json_checks = [i for i in data["items"] if i["category"] == "Configurações JSON"]
        assert len(json_checks) >= 5
        assert all(i["status"] == "OK" for i in json_checks)

    def test_f13_healthcheck_evaluates_lifecycle_hooks(self):
        proc = subprocess.run(
            [sys.executable, str(HEALTHCHECK_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        data = json.loads(proc.stdout)
        hook_checks = [i for i in data["items"] if i["category"] == "Lifecycle Hooks"]
        assert len(hook_checks) >= 2
        assert any(i["name"] == "pre_tool_guard.py" and i["status"] == "OK" for i in hook_checks)

    def test_f13_healthcheck_human_readable_output(self):
        proc = subprocess.run(
            [sys.executable, str(HEALTHCHECK_SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "ANTIGRAVITY ECOSYSTEM HEALTHCHECK" in proc.stdout


# ============================================================================
# Feature 14: Ecosystem Healthcheck Unit Test Suite
# ============================================================================

class TestFeature14EcosystemHealthcheckUnitTestSuite:
    """Valida a presença e integridade da suíte de testes unitários em tests/unit/."""

    def test_f14_hooks_unit_tests_exist(self):
        test_file = WORKSPACE_ROOT / "tests" / "unit" / "test_hooks.py"
        assert test_file.exists()

    def test_f14_project_resolver_unit_tests_exist(self):
        test_file = WORKSPACE_ROOT / "tests" / "unit" / "test_project_resolver.py"
        assert test_file.exists()

    def test_f14_skills_healthcheck_unit_tests_exist(self):
        test_file = WORKSPACE_ROOT / "tests" / "unit" / "test_skills_healthcheck.py"
        assert test_file.exists()

    def test_f14_windows_setup_unit_tests_exist(self):
        test_file = WORKSPACE_ROOT / "tests" / "unit" / "test_windows_setup.py"
        assert test_file.exists()

    def test_f14_all_unit_tests_collectable(self):
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/unit", "--collect-only", "-q"],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0, f"Falha na coleta de testes unitários: {proc.stderr}"
        assert "tests collected" in proc.stdout
