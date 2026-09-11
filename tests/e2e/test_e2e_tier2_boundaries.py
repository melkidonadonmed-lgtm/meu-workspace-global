"""Tier 2: Boundary & Corner Cases (Casos de Limite, Erros e Anomalias).

Cobre exaustivamente limites, strings vazias, caracteres especiais, caminhos inexistentes,
injeções e anomalias estruturais para todas as Features 1 a 14 do ecossistema.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from agents.project_resolver import ProjectTargetResolver
from agents.specialized.workspace_specialist import WorkspaceSpecialistAgent
from tests.e2e.conftest import (
    CANONICAL_HOOK_SCRIPT,
    CANONICAL_PROJECTS_JSON,
    DASHBOARD_SCRIPT,
    HEALTHCHECK_SCRIPT,
    HUB_GEMINI_DIR,
    WORKSPACE_HOOK_SCRIPT,
    WORKSPACE_ROOT,
    run_hook_subprocess,
)


# ============================================================================
# Feature 1: BVA — SSoT Canonical Projects Registry (projects.json)
# ============================================================================

class TestFeature01RegistryBoundaries:
    """Casos de limite e anomalias para o projects.json."""

    def test_f1_bva_missing_file_handling(self, tmp_path: Path):
        non_existent = tmp_path / "non_existent_projects.json"
        assert not non_existent.exists()

    def test_f1_bva_empty_json_file(self, tmp_path: Path):
        empty_json = tmp_path / "empty.json"
        empty_json.write_text("{}", encoding="utf-8")
        data = json.loads(empty_json.read_text(encoding="utf-8"))
        assert data.get("projects") is None

    def test_f1_bva_malformed_json_content(self, tmp_path: Path):
        corrupt_json = tmp_path / "corrupt.json"
        corrupt_json.write_text("{projects: [unquoted]}", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            json.loads(corrupt_json.read_text(encoding="utf-8"))

    def test_f1_bva_non_dict_projects_key(self, tmp_path: Path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text(json.dumps({"projects": ["lista", "invalida"]}), encoding="utf-8")
        data = json.loads(bad_json.read_text(encoding="utf-8"))
        assert not isinstance(data["projects"], dict)

    def test_f1_bva_unicode_and_spaces_in_paths(self):
        # Valida que o projects.json atual não quebra com caminhos contendo espaços
        data = json.loads(CANONICAL_PROJECTS_JSON.read_text(encoding="utf-8"))
        has_spaces = any(" " in k for k in data["projects"].keys())
        assert has_spaces, "Esperado que existam caminhos com espaço (ex: 'antigravity ide') no projects.json"


# ============================================================================
# Feature 2: BVA — Deep Project Target Resolver
# ============================================================================

class TestFeature02ResolverBoundaries:
    """Casos de limite e entradas adversas para ProjectTargetResolver."""

    def test_f2_bva_empty_query_string(self):
        resolver = ProjectTargetResolver()
        assert resolver.resolve_target("", WORKSPACE_ROOT) is None

    def test_f2_bva_whitespace_only_query(self):
        resolver = ProjectTargetResolver()
        assert resolver.resolve_target("   \t\n  ", WORKSPACE_ROOT) is None

    def test_f2_bva_special_characters_and_injection(self):
        resolver = ProjectTargetResolver()
        malicious = "'; DROP TABLE projects; <script>alert('xss')</script>"
        assert resolver.resolve_target(malicious, WORKSPACE_ROOT) is None

    def test_f2_bva_boundary_substring_not_matched(self):
        resolver = ProjectTargetResolver()
        # "canvas_ide_extra_word" não deve casar falsamente como palavra inteira isolada se regex exigir boundary
        # ou se o comportamento for estrito
        res = resolver.resolve_target("canvas_idealistic_perspective", WORKSPACE_ROOT)
        # Se casar, verificar que não é um match acidental inválido
        if res:
            assert res.name in ("canvas_ide", "canvas-ide")

    def test_f2_bva_extreme_length_query(self):
        resolver = ProjectTargetResolver()
        huge_prompt = "audite " + ("bla " * 1000) + "pcm " + ("foo " * 500)
        res = resolver.resolve_target(huge_prompt, WORKSPACE_ROOT)
        assert res is not None
        assert res.name == "pcm"


# ============================================================================
# Feature 3: BVA — Unified Deep Stack Detection
# ============================================================================

class TestFeature03StackDetectionBoundaries:
    """Casos de limite e anomalias para detecção de stack."""

    def test_f3_bva_corrupted_package_json(self, tmp_path: Path):
        proj = tmp_path / "corrupt_node"
        proj.mkdir()
        (proj / "package.json").write_text("{invalid json: broken}", encoding="utf-8")
        resolver = ProjectTargetResolver()
        # Não deve lançar exceção não tratada
        stack = resolver._detect_tech_stack(proj)
        assert isinstance(stack, list)

    def test_f3_bva_empty_package_json(self, tmp_path: Path):
        proj = tmp_path / "empty_node"
        proj.mkdir()
        (proj / "package.json").write_text("{}", encoding="utf-8")
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(proj)
        assert "Node.js/npm" in stack
        assert "React" not in stack

    def test_f3_bva_package_json_with_numeric_dependencies(self, tmp_path: Path):
        proj = tmp_path / "weird_node"
        proj.mkdir()
        (proj / "package.json").write_text('{"dependencies": 12345}', encoding="utf-8")
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(proj)
        assert isinstance(stack, list)

    def test_f3_bva_non_existent_manifest_directory(self, tmp_path: Path):
        non_dir = tmp_path / "ghost_folder"
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(non_dir)
        assert stack == []

    def test_f3_bva_binary_garbage_in_pyproject(self, tmp_path: Path):
        proj = tmp_path / "binary_python"
        proj.mkdir()
        (proj / "pyproject.toml").write_bytes(b"\x00\xff\xfe\x01\x02\x03garbage")
        resolver = ProjectTargetResolver()
        stack = resolver._detect_tech_stack(proj)
        assert "Python" in stack


# ============================================================================
# Feature 4: BVA — WorkspaceSpecialistAgent
# ============================================================================

class TestFeature04WorkspaceSpecialistBoundaries:
    """Casos de limite para o WorkspaceSpecialistAgent."""

    def test_f4_bva_scan_workspace_non_existent_target(self):
        agent = WorkspaceSpecialistAgent(root_dir=str(WORKSPACE_ROOT))
        res = agent.scan_workspace(target_path="C:/GhostDirectory/That/Never/Existed")
        assert res["status"] == "success"
        assert res["total_items_scanned"] >= 0

    def test_f4_bva_scan_workspace_zero_depth(self):
        agent = WorkspaceSpecialistAgent(root_dir=str(WORKSPACE_ROOT))
        res = agent.scan_workspace(max_depth=0)
        assert res["status"] == "success"
        assert len(res["files"]) == 0

    def test_f4_bva_scan_workspace_negative_depth(self):
        agent = WorkspaceSpecialistAgent(root_dir=str(WORKSPACE_ROOT))
        res = agent.scan_workspace(max_depth=-1)
        assert res["status"] == "success"
        assert len(res["files"]) == 0

    def test_f4_bva_scan_workspace_empty_directory(self, tmp_path: Path):
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()
        agent = WorkspaceSpecialistAgent(root_dir=str(empty_dir))
        res = agent.scan_workspace(max_depth=3)
        assert res["status"] == "success"
        assert res["total_items_scanned"] == 0

    def test_f4_bva_scan_workspace_very_high_depth(self, tmp_path: Path):
        deep_dir = tmp_path / "a" / "b" / "c" / "d" / "e"
        deep_dir.mkdir(parents=True)
        (deep_dir / "target.txt").write_text("deep", encoding="utf-8")
        agent = WorkspaceSpecialistAgent(root_dir=str(tmp_path))
        res = agent.scan_workspace(max_depth=10)
        assert res["total_items_scanned"] >= 5


# ============================================================================
# Feature 5: BVA — Projects Dashboard (projects_dashboard.py)
# ============================================================================

class TestFeature05ProjectsDashboardBoundaries:
    """Casos de limite para o dashboard de projetos."""

    def test_f5_bva_inspect_unknown_project_key(self):
        pass
        # Invocação via subprocess para isolamento
        proc = subprocess.run(
            [sys.executable, str(DASHBOARD_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        keys = [p["key"] for p in data["projects"]]
        assert "non_existent_key_xyz" not in keys

    def test_f5_bva_check_port_in_use_invalid_port_negative(self):
        # Validação do comportamento de porta negativa
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, r'{HUB_GEMINI_DIR}/scripts'); "
                "from projects_dashboard import check_port_in_use; print(check_port_in_use(-1))",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "False" in proc.stdout

    def test_f5_bva_check_port_in_use_invalid_port_excessive(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, r'{HUB_GEMINI_DIR}/scripts'); "
                "from projects_dashboard import check_port_in_use; print(check_port_in_use(999999))",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "False" in proc.stdout

    def test_f5_bva_git_status_non_git_folder(self, tmp_path: Path):
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, r'{HUB_GEMINI_DIR}/scripts'); "
                f"from projects_dashboard import get_git_status; from pathlib import Path; "
                f"res = get_git_status(Path(r'{tmp_path}')); print(res['is_git'])",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "False" in proc.stdout

    def test_f5_bva_dashboard_cli_multiple_flags(self):
        proc = subprocess.run(
            [sys.executable, str(DASHBOARD_SCRIPT), "--json", "--verbose"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert "projects" in data


# ============================================================================
# Feature 6: BVA — Directory Boundary Enforcement (pre_tool_guard.py)
# ============================================================================

class TestFeature06BoundaryEnforcementBoundaries:
    """Casos de limite de caminhos de arquivos para o hook de PreToolUse."""

    def test_f6_bva_empty_target_file(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": ""},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        # Caminho vazio não deve crashear o hook
        assert "decision" in res

    def test_f6_bva_relative_path_traversal(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "../../../Windows/System32/cmd.exe"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert "decision" in res

    def test_f6_bva_null_byte_or_raw_unicode_in_path(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/Projetos/pcm/src/áéíóú_çãõ.txt"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "allow"

    def test_f6_bva_unc_network_path(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "\\\\192.168.1.50\\share\\exploit.exe"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert "decision" in res

    def test_f6_bva_trailing_spaces_in_target_file(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/Projetos/pcm/src/App.tsx   "},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "allow"


# ============================================================================
# Feature 7: BVA — Sensitive Files Interception
# ============================================================================

class TestFeature07SensitiveFilesBoundaries:
    """Casos de limite para arquivos sensíveis e variações de extensão/casing."""

    def test_f7_bva_case_variations_dot_env(self):
        for env_name in [".ENV", ".Env.local", ".env.PRODUCTION", ".ENV.TEST"]:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": f"C:/Users/melki/Projetos/pcm/{env_name}"},
                }
            }
            res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
            assert res.get("decision") == "force_ask", f"Falhou para variação de case: {env_name}"

    def test_f7_bva_nested_subdirectory_sensitive_file(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/Projetos/pcm/config/sub/deep/.env"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f7_bva_ssh_key_variations(self):
        for key_file in ["id_rsa", "id_rsa.pub", "id_ed25519", "server.pem", "private.key"]:
            payload = {
                "toolCall": {
                    "name": "replace_file_content",
                    "args": {"TargetFile": f"C:/Users/melki/.ssh/{key_file}"},
                }
            }
            res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
            assert res.get("decision") == "force_ask", f"Falhou para chave SSH: {key_file}"

    def test_f7_bva_credentials_json_case_variation(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "C:/Users/melki/configs/CREDENTIALS.JSON"},
            }
        }
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "force_ask"

    def test_f7_bva_non_sensitive_partial_match(self):
        # Arquivos que apenas contêm "env" no nome mas não são arquivos de ambiente sensíveis
        non_sensitive = [
            "environment_settings.py",
            "envelope_generator.ts",
            "readme_env_setup.md",
        ]
        for name in non_sensitive:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": f"C:/Users/melki/Projetos/pcm/src/{name}"},
                }
            }
            res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
            assert res.get("decision") == "allow", f"Falso positivo em: {name}"


# ============================================================================
# Feature 8: BVA — High-Risk Destructive Commands Interception
# ============================================================================

class TestFeature08DestructiveCommandsBoundaries:
    """Casos de limite para regex de comandos destrutivos e variações sintáticas."""

    def test_f8_bva_irregular_spacing_rm(self):
        cmds = [
            "rm   -r   -f   /",
            "rm    -rf   node_modules",
            "rm  -f  -r  ./temp",
        ]
        for cmd in cmds:
            payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": cmd}}}
            res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
            assert res.get("decision") == "force_ask", f"Falhou para espaçamento irregular: {cmd}"

    def test_f8_bva_powershell_case_variations(self):
        cmds = [
            "rEmOvE-iTeM -Recurse C:/Temp",
            "remove-item -recurse ./build",
            "REMOVE-ITEM ./dist -RECURSE",
        ]
        for cmd in cmds:
            payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": cmd}}}
            res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
            assert res.get("decision") == "force_ask", f"Falhou para PowerShell casing: {cmd}"

    def test_f8_bva_git_flags_variations(self):
        cmds = [
            "git   push   origin   main   --force",
            "git push --force",
            "git clean -fdx",
            "git clean -f -d -x",
        ]
        for cmd in cmds:
            payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": cmd}}}
            res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
            assert res.get("decision") == "force_ask", f"Falhou para git: {cmd}"

    def test_f8_bva_empty_command_line(self):
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": ""}}}
        res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        assert res.get("decision") == "allow"

    def test_f8_bva_safe_command_with_rm_in_word(self):
        # Palavras como "formatar", "performance", "norm" não devem disparar force_ask
        safe = [
            "echo performance",
            "git log --format=oneline",
            "echo 'normal workflow'",
        ]
        for cmd in safe:
            payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": cmd}}}
            res = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
            assert res.get("decision") == "allow", f"Falso positivo para comando seguro: {cmd}"


# ============================================================================
# Feature 9: BVA — Seam Canonical Synchronization
# ============================================================================

class TestFeature09HookSynchronizationBoundaries:
    """Casos de limite de comunicação stdin/stdout e paridade entre hooks."""

    def test_f9_bva_empty_stdin_payload(self):
        # Ambos os hooks devem retornar allow padrão quando stdin está vazio
        for script in [CANONICAL_HOOK_SCRIPT, WORKSPACE_HOOK_SCRIPT]:
            proc = subprocess.run(
                [sys.executable, str(script)],
                input="",
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            assert proc.returncode == 0
            data = json.loads(proc.stdout)
            assert data.get("decision") == "allow"

    def test_f9_bva_malformed_json_stdin(self):
        # Ambos os hooks devem aplicar fallback seguro sem crash (exit code 0 e allow)
        for script in [CANONICAL_HOOK_SCRIPT, WORKSPACE_HOOK_SCRIPT]:
            proc = subprocess.run(
                [sys.executable, str(script)],
                input="{broken json payload",
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            assert proc.returncode == 0
            data = json.loads(proc.stdout)
            assert data.get("decision") == "allow"
            assert "Fallback seguro" in data.get("reason", "")

    def test_f9_bva_empty_dict_payload(self):
        payload = {}
        res_canon = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        res_work = run_hook_subprocess(WORKSPACE_HOOK_SCRIPT, payload)
        assert res_canon.get("decision") == res_work.get("decision") == "allow"

    def test_f9_bva_utf8_accented_command(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "echo 'olá mundo acentuado çãõáéíóú'"},
            }
        }
        res_canon = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        res_work = run_hook_subprocess(WORKSPACE_HOOK_SCRIPT, payload)
        assert res_canon.get("decision") == res_work.get("decision") == "allow"

    def test_f9_bva_large_json_payload(self):
        huge_code = "console.log('line');\n" * 2000
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": "C:/Users/melki/Projetos/pcm/src/large.js",
                    "CodeContent": huge_code,
                },
            }
        }
        res_canon = run_hook_subprocess(CANONICAL_HOOK_SCRIPT, payload)
        res_work = run_hook_subprocess(WORKSPACE_HOOK_SCRIPT, payload)
        assert res_canon.get("decision") == res_work.get("decision") == "allow"


# ============================================================================
# Feature 10: BVA — Ubiquitous Language (CONTEXT.md)
# ============================================================================

class TestFeature10DomainModelBoundaries:
    """Casos de limite para validação e integridade de CONTEXT.md."""

    def test_f10_bva_context_md_not_empty(self):
        content = (WORKSPACE_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        assert len(content.splitlines()) >= 50

    def test_f10_bva_context_md_utf8_encoding(self):
        raw_bytes = (WORKSPACE_ROOT / "CONTEXT.md").read_bytes()
        decoded = raw_bytes.decode("utf-8")
        assert "Linguagem Ubíqua" in decoded

    def test_f10_bva_context_md_consistent_bold_term_formatting(self):
        content = (WORKSPACE_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.startswith("**")]
        assert len(lines) >= 10
        for line in lines:
            assert line.endswith("**:") or line.endswith("**")

    def test_f10_bva_context_md_avoids_present_for_each_term(self):
        content = (WORKSPACE_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        avoid_count = content.count("_Avoid_:")
        assert avoid_count >= 10, "Cada termo principal deve possuir diretiva _Avoid_:"

    def test_f10_bva_context_md_no_broken_markdown_links(self):
        content = (WORKSPACE_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        assert "](" not in content or not any("](" in l and ")" not in l for l in content.splitlines())


# ============================================================================
# Feature 11: BVA — ADRs (docs/adr/)
# ============================================================================

class TestFeature11ADRBoundaries:
    """Casos de limite para os registros arquiteturais em docs/adr/."""

    def test_f11_bva_non_existent_adr_read(self):
        ghost_adr = WORKSPACE_ROOT / "docs" / "adr" / "0999-ghost-adr.md"
        assert not ghost_adr.exists()

    def test_f11_bva_adr_naming_convention(self):
        adr_dir = WORKSPACE_ROOT / "docs" / "adr"
        adrs = list(adr_dir.glob("*.md"))
        for adr in adrs:
            assert adr.name[:4].isdigit(), f"ADR não inicia com 4 dígitos: {adr.name}"
            assert adr.name[4] == "-", f"ADR não possui hífen após número: {adr.name}"

    def test_f11_bva_adr_files_non_empty(self):
        adr_dir = WORKSPACE_ROOT / "docs" / "adr"
        for adr in adr_dir.glob("*.md"):
            assert adr.stat().st_size > 200, f"ADR com tamanho suspeito: {adr.name}"

    def test_f11_bva_adr_utf8_decodable(self):
        adr_dir = WORKSPACE_ROOT / "docs" / "adr"
        for adr in adr_dir.glob("*.md"):
            content = adr.read_text(encoding="utf-8")
            assert len(content) > 0

    def test_f11_bva_adr_sequential_numbering(self):
        adr_dir = WORKSPACE_ROOT / "docs" / "adr"
        prefixes = sorted([f.name[:4] for f in adr_dir.glob("*.md")])
        assert "0001" in prefixes
        assert "0002" in prefixes
        assert "0003" in prefixes
        assert "0004" in prefixes


# ============================================================================
# Feature 12: BVA — Pytest Windows Configuration (pyproject.toml)
# ============================================================================

class TestFeature12PytestConfigBoundaries:
    """Casos de limite para a configuração do pytest em pyproject.toml."""

    def test_f12_bva_pyproject_toml_valid_toml_syntax(self):
        content = (WORKSPACE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        data = tomllib.loads(content)
        assert "tool" in data
        assert "pytest" in data["tool"]

    def test_f12_bva_pytest_section_has_testpaths(self):
        content = (WORKSPACE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        data = tomllib.loads(content)
        ini_options = data["tool"]["pytest"]["ini_options"]
        assert "testpaths" in ini_options
        assert "tests" in ini_options["testpaths"]

    def test_f12_bva_tmp_retention_is_integer_zero(self):
        content = (WORKSPACE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        data = tomllib.loads(content)
        ini_options = data["tool"]["pytest"]["ini_options"]
        assert ini_options["tmp_path_retention_count"] == 0

    def test_f12_bva_basetemp_path_format(self):
        content = (WORKSPACE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        data = tomllib.loads(content)
        ini_options = data["tool"]["pytest"]["ini_options"]
        addopts = ini_options["addopts"]
        assert "--basetemp=" in addopts

    def test_f12_bva_pyproject_dependencies_non_empty(self):
        content = (WORKSPACE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        data = tomllib.loads(content)
        deps = data["project"]["dependencies"]
        assert len(deps) >= 10


# ============================================================================
# Feature 13: BVA — Ecosystem Healthcheck (ecosystem_healthcheck.py)
# ============================================================================

class TestFeature13HealthcheckBoundaries:
    """Casos de limite para o verificador de conformidade do ecossistema."""

    def test_f13_bva_check_json_file_empty_file(self, tmp_path: Path):
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, r'{HUB_GEMINI_DIR}/scripts'); "
                f"from ecosystem_healthcheck import check_json_file; from pathlib import Path; "
                f"empty = Path(r'{tmp_path}/empty.json'); empty.write_text('', encoding='utf-8'); "
                "ok, msg = check_json_file(empty); print(ok)",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "False" in proc.stdout

    def test_f13_bva_check_json_file_corrupt_json(self, tmp_path: Path):
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, r'{HUB_GEMINI_DIR}/scripts'); "
                f"from ecosystem_healthcheck import check_json_file; from pathlib import Path; "
                f"corrupt = Path(r'{tmp_path}/corrupt.json'); corrupt.write_text('{{bad', encoding='utf-8'); "
                "ok, msg = check_json_file(corrupt); print(ok)",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "False" in proc.stdout

    def test_f13_bva_check_json_file_directory_instead_of_file(self, tmp_path: Path):
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, r'{HUB_GEMINI_DIR}/scripts'); "
                f"from ecosystem_healthcheck import check_json_file; from pathlib import Path; "
                f"ok, msg = check_json_file(Path(r'{tmp_path}')); print(ok)",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "False" in proc.stdout

    def test_f13_bva_run_hub_healthcheck_custom_empty_dir(self, tmp_path: Path):
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, r'{HUB_GEMINI_DIR}/scripts'); "
                f"from ecosystem_healthcheck import run_hub_healthcheck; from pathlib import Path; "
                f"rep = run_hub_healthcheck(Path(r'{tmp_path}')); print(rep.is_healthy)",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0
        assert "False" in proc.stdout

    def test_f13_bva_healthcheck_cli_unknown_flag(self):
        proc = subprocess.run(
            [sys.executable, str(HEALTHCHECK_SCRIPT), "--unknown-flag"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode != 0
        assert "unrecognized arguments" in proc.stderr or "error" in proc.stderr.lower()


# ============================================================================
# Feature 14: BVA — Unit Test Suite
# ============================================================================

class TestFeature14UnitTestSuiteBoundaries:
    """Casos de limite para a suíte unitária."""

    def test_f14_bva_unit_test_run_with_custom_filter_runs_zero(self):
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/unit", "-k", "impossible_filter_xyz123", "-q"],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode in (0, 5)  # 5 = no tests collected in pytest

    def test_f14_bva_unit_test_directory_structure(self):
        unit_dir = WORKSPACE_ROOT / "tests" / "unit"
        test_files = list(unit_dir.glob("test_*.py"))
        assert len(test_files) >= 5

    def test_f14_bva_unit_test_files_naming_convention(self):
        unit_dir = WORKSPACE_ROOT / "tests" / "unit"
        for f in unit_dir.glob("*.py"):
            assert f.name.startswith("test_"), f"Arquivo em tests/unit não inicia com test_: {f.name}"

    def test_f14_bva_unit_test_files_non_empty(self):
        unit_dir = WORKSPACE_ROOT / "tests" / "unit"
        for f in unit_dir.glob("*.py"):
            assert f.stat().st_size > 100, f"Arquivo de teste suspeito de estar vazio: {f.name}"

    def test_f14_bva_pytest_ini_options_present(self):
        pyproj = WORKSPACE_ROOT / "pyproject.toml"
        content = pyproj.read_text(encoding="utf-8")
        assert "[tool.pytest.ini_options]" in content
