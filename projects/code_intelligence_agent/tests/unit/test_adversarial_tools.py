"""Testes adversariais, oráculos e estresse para as ferramentas determinísticas em app/tools.py.

Executado pelo Challenger M1 para verificação empírica e rigorosa de hipóteses de falha,
casos de borda e robustez contra inputs maliciosos/inválidos.
"""

from pathlib import Path

from app.tools import (
    analyze_ast_anomalies,
    generate_unified_patch,
    inspect_directory,
    read_code_file,
)

# ============================================================================
# 1. Testes de Borda e Adversariais: analyze_ast_anomalies
# ============================================================================


def test_analyze_ast_deeply_invalid_syntax_variations(tmp_path: Path) -> None:
    """Testa variações profundas de código sintaticamente inválido."""
    cases = [
        ("unbalanced_parens.py", "x = (((1 + 2) * 3\n"),
        ("indentation_error.py", "def foo():\nreturn 42\n"),
        ("incomplete_try.py", "try:\n    x = 1\n"),
        ("invalid_tokens.py", "def $$$$bad_func():\n    pass\n"),
        ("double_colon.py", "if True::\n    pass\n"),
    ]

    for filename, code in cases:
        file_path = tmp_path / filename
        file_path.write_text(code, encoding="utf-8")

        res = analyze_ast_anomalies(str(file_path))

        assert res["status"] == "syntax_error", f"Falhou para {filename}"
        assert res["is_valid_syntax"] is False
        assert res["syntax_error"] is not None
        assert res["metrics"]["total_anomalies"] == 1
        assert res["anomalies"][0]["type"] == "syntax_error"
        assert res["anomalies"][0]["severity"] == "critical"


def test_analyze_ast_complex_except_handlers_matrix(tmp_path: Path) -> None:
    """Testa matriz completa de handlers except: nus, genéricos, específicos e suprimidos."""
    complex_code = """
import sys

def test_exceptions():
    # 1. Bare except -> deve gerar anomalia bare_except
    try:
        x = 1
    except:
        pass

    # 2. Generic except sem noqa -> deve gerar generic_except
    try:
        y = 2
    except Exception:
        pass

    # 3. Generic except com supressão BLE001 -> NÃO deve gerar anomalia
    try:
        z = 3
    except Exception as e:  # noqa: BLE001
        print(e)

    # 4. Bare except com supressão bare-except -> is_suppressed True
    try:
        w = 4
    except:  # noqa: bare-except
        pass

    # 5. Handler específico -> NÃO deve gerar anomalia
    try:
        v = int("abc")
    except ValueError:
        pass

    # 6. Tupla de exceções específicas -> NÃO deve gerar anomalia
    try:
        d = {}
        _ = d["foo"]
    except (KeyError, IndexError, TypeError) as err:
        pass
"""
    file_path = tmp_path / "except_matrix.py"
    file_path.write_text(complex_code, encoding="utf-8")

    res = analyze_ast_anomalies(str(file_path))

    assert res["status"] == "success"
    assert res["is_valid_syntax"] is True

    bare_excepts = [a for a in res["anomalies"] if a["type"] == "bare_except"]
    generic_excepts = [a for a in res["anomalies"] if a["type"] == "generic_except"]

    # Deve ter encontrado 2 bare excepts (um sem supressão e um com)
    assert len(bare_excepts) == 2
    assert bare_excepts[0]["suppressed"] is False
    assert bare_excepts[1]["suppressed"] is True

    # Deve ter encontrado exatamente 1 generic_except não suprimido
    assert len(generic_excepts) == 1
    assert generic_excepts[0]["suppressed"] is False


def test_analyze_ast_mccabe_exact_decision_counting(tmp_path: Path) -> None:
    """Verifica com precisão matemática a contagem de nós de decisão de McCabe.

    Fórmula: McCabe = 1 + nós_de_decisão
    Decisões testadas:
    - 1 if (+1)
    - 2 elif (+2)
    - 1 for (+1)
    - 1 while (+1)
    - 1 ifexp (ternário) (+1)
    - 1 assert (+1)
    - 1 except handler (+1)
    - 1 if com boolop de 3 operandos: 1 do if + 2 do BoolOp (3 - 1) = (+3)
    Esperado total: 1 (base) + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 3 = 12.
    """
    code = """
def funcao_oraculo(a, b, c, d):
    res = 0
    if a > 0:           # +1
        res += 1
    elif a < -10:       # +1
        res -= 1
    elif a == 0:        # +1
        res += 2

    for i in range(b):  # +1
        res += i

    while c > 0:        # +1
        c -= 1

    x = 10 if d else 20 # +1

    assert x > 0        # +1

    try:
        res += 1
    except ValueError:  # +1
        pass

    if a and b and c:   # +3 (1 do if + 2 do BoolOp)
        res += 100

    return res
"""
    file_path = tmp_path / "mccabe_oracle.py"
    file_path.write_text(code, encoding="utf-8")

    res = analyze_ast_anomalies(str(file_path))

    assert res["status"] == "success"
    assert len(res["functions"]) == 1

    fn_meta = res["functions"][0]
    assert fn_meta["name"] == "funcao_oraculo"
    assert fn_meta["mccabe_complexity"] == 12

    # Como complexidade é 12 (> 10), deve registrar anomalia high_complexity
    mccabe_anomalies = [a for a in res["anomalies"] if a["type"] == "high_complexity"]
    assert len(mccabe_anomalies) == 1
    assert mccabe_anomalies[0]["complexity"] == 12


def test_analyze_ast_mccabe_nested_functions_isolation(tmp_path: Path) -> None:
    """Garante que funções aninhadas (closures/inner) NÃO somam sua complexidade na função externa."""
    code = """
def outer_function(x):
    # Decisão na externa: 1 if (+1) -> McCabe externa = 2
    if x > 10:
        print("maior")

    def inner_function(y):
        # Decisões na interna: if (+1), elif (+1), while (+1) -> McCabe interna = 4
        if y == 1:
            return 10
        elif y == 2:
            return 20
        while y > 0:
            y -= 1
        return 0

    return inner_function(x)
"""
    file_path = tmp_path / "nested_functions.py"
    file_path.write_text(code, encoding="utf-8")

    res = analyze_ast_anomalies(str(file_path))

    assert res["status"] == "success"
    assert len(res["functions"]) == 2

    funcs_by_name = {f["name"]: f for f in res["functions"]}
    assert funcs_by_name["outer_function"]["mccabe_complexity"] == 2
    assert funcs_by_name["inner_function"]["mccabe_complexity"] == 4
    # Nenhuma deve exceder 10
    assert not any(a["type"] == "high_complexity" for a in res["anomalies"])


def test_analyze_ast_clean_idiomatic_code(tmp_path: Path) -> None:
    """Garante que código limpo, moderno e idiomático tenha zero anomalias."""
    clean_code = '''"""Módulo exemplar."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Item:
    id: int
    name: str
    description: Optional[str] = None

class ItemService:
    def __init__(self) -> None:
        self._items: dict[int, Item] = {}

    def add_item(self, item: Item) -> None:
        self._items[item.id] = item

    def get_item(self, item_id: int) -> Optional[Item]:
        return self._items.get(item_id)
'''
    file_path = tmp_path / "clean_service.py"
    file_path.write_text(clean_code, encoding="utf-8")

    res = analyze_ast_anomalies(str(file_path))

    assert res["status"] == "success"
    assert res["is_valid_syntax"] is True
    assert res["metrics"]["total_anomalies"] == 0
    assert len(res["classes"]) == 2
    assert len(res["functions"]) == 3


def test_analyze_ast_empty_file_and_missing_file(tmp_path: Path) -> None:
    """Verifica comportamento com arquivo vazio e inexistente."""
    empty_file = tmp_path / "zero_bytes.py"
    empty_file.write_text("", encoding="utf-8")

    res_empty = analyze_ast_anomalies(str(empty_file))
    assert res_empty["status"] == "success"
    assert res_empty["is_valid_syntax"] is True
    assert res_empty["metrics"]["total_anomalies"] == 0
    assert res_empty["metrics"]["total_functions"] == 0

    res_missing = analyze_ast_anomalies(str(tmp_path / "non_existent_file.py"))
    assert res_missing["status"] == "error"
    assert res_missing["error"] == "FILE_NOT_FOUND"


# ============================================================================
# 2. Testes Adversariais: generate_unified_patch
# ============================================================================


def test_generate_unified_patch_dry_run_rejection_matrix(tmp_path: Path) -> None:
    """Submete múltiplos patches com anomalias de sintaxe e garante inviolabilidade do disco."""
    original_code = "def calcular(val):\n    res = val * 10\n    return res\n"
    target_file = tmp_path / "protected_target.py"
    target_file.write_text(original_code, encoding="utf-8")

    bad_snippets = [
        "    res = val * 10 %%% invalid",
        "    res = (((val * 10)",
        "def broken_syntax(:\n    pass",
        "    res = val * 10\nreturn res",  # IndentationError
        "    class 123BadClass:\n        pass",
    ]

    for idx, bad_replacement in enumerate(bad_snippets):
        res = generate_unified_patch(
            str(target_file),
            original_snippet="    res = val * 10",
            replacement_snippet=bad_replacement,
        )

        assert res["status"] == "rejected", f"Deveria ter rejeitado caso {idx}: {bad_replacement}"
        assert res["applied"] is False
        assert res["changes_made"] is False
        assert res["error"] == "SYNTAX_ERROR"
        assert "syntax_error" in res

        # Verificação do disco: estritamente intocado!
        disk_content = target_file.read_text(encoding="utf-8")
        assert disk_content == original_code


def test_generate_unified_patch_target_not_found_variations(tmp_path: Path) -> None:
    """Testa tentativas de substituição com trechos inexistentes ou ligeiramente divergentes."""
    target_file = tmp_path / "snippet_test.py"
    target_file.write_text("def somar(a, b):\n    return a + b\n", encoding="utf-8")

    divergent_snippets = [
        "return a - b",          # Operador inexistente
        "def subtrair(a, b):",  # Função não existe
        "def somar(x, y):",      # Argumentos diferentes
    ]

    for snippet in divergent_snippets:
        res = generate_unified_patch(
            str(target_file),
            original_snippet=snippet,
            replacement_snippet="    return a * b",
        )
        assert res["status"] == "error"
        assert res["error"] == "TARGET_NOT_FOUND"
        assert res["applied"] is False


def test_generate_unified_patch_perfect_unified_diff_format(tmp_path: Path) -> None:
    """Verifica se o diff gerado segue com fidelidade as especificações do Unified Diff."""
    target_file = tmp_path / "diff_format.py"
    initial_content = "def saudar(nome):\n    msg = f'Ola, {nome}'\n    return msg\n"
    # Grava explicitamente com bytes LF para garantir correspondência no diff
    target_file.write_bytes(initial_content.encode("utf-8"))

    orig_snippet = "    msg = f'Ola, {nome}'\n    return msg"
    repl_snippet = "    # Formata saudacao formal\n    return f'Prezado(a) {nome}'"

    res = generate_unified_patch(str(target_file), orig_snippet, repl_snippet)

    assert res["status"] == "applied"
    assert res["applied"] is True
    assert res["changes_made"] is True

    diff = res["diff"]
    assert "--- a/diff_format.py" in diff
    assert "+++ b/diff_format.py" in diff
    assert "-    msg = f'Ola, {nome}'" in diff
    assert "-    return msg" in diff
    assert "+    # Formata saudacao formal" in diff
    assert "+    return f'Prezado(a) {nome}'" in diff

    # Confere persistência no disco
    on_disk = target_file.read_text(encoding="utf-8")
    assert "Prezado(a)" in on_disk
    assert "Ola" not in on_disk


def test_generate_unified_patch_no_temp_files_leaked(tmp_path: Path) -> None:
    """Garante que nenhum arquivo temporário de escrita atômica permanece no diretório."""
    target_file = tmp_path / "leak_test.py"
    target_file.write_bytes(b"x = 1\n")

    res = generate_unified_patch(str(target_file), "x = 1", "x = 2")
    assert res["status"] == "applied"

    # Não deve existir nenhum arquivo .tmp_* no diretório
    tmp_files = list(tmp_path.glob("*.tmp_*"))
    assert len(tmp_files) == 0


# ============================================================================
# 3. Testes de Navegação e Leitura: inspect_directory e read_code_file
# ============================================================================


def test_inspect_directory_windows_path_compatibility(tmp_path: Path) -> None:
    """Verifica compatibilidade de inspect_directory com caminhos com barras normais e invertidas no Windows."""
    repo = tmp_path / "repo_nav"
    repo.mkdir()
    (repo / "file1.py").write_text("# f1", encoding="utf-8")

    # Caminho com forward slashes (/)
    fwd_path = repo.as_posix()
    res_fwd = inspect_directory(fwd_path, max_depth=2)
    assert res_fwd["status"] == "success"
    assert res_fwd["total_files"] == 1

    # Caminho com backslashes (\)
    back_path = str(repo).replace("/", "\\")
    res_back = inspect_directory(back_path, max_depth=2)
    assert res_back["status"] == "success"
    assert res_back["total_files"] == 1


def test_inspect_directory_prunes_all_noisy_directories(tmp_path: Path) -> None:
    """Cria TODAS as pastas da lista PRUNE_DIRS e garante que são estritamente podadas."""
    repo = tmp_path / "prune_repo"
    repo.mkdir()

    noisy_dirs = [
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".pytest_cache",
        ".ruff_cache",
        ".brain",
        "dist",
        "build",
    ]

    for nd in noisy_dirs:
        nd_path = repo / nd
        nd_path.mkdir()
        (nd_path / "dummy.txt").write_text("dummy", encoding="utf-8")

    # Pasta legítima
    legit_dir = repo / "legit_src"
    legit_dir.mkdir()
    (legit_dir / "app.py").write_text("print('ok')", encoding="utf-8")

    res = inspect_directory(str(repo), max_depth=5)

    assert res["status"] == "success"
    assert res["total_files"] == 1
    assert res["total_directories"] == 1

    rel_paths = [e["relative_path"] for e in res["entries"]]
    for nd in noisy_dirs:
        for p in rel_paths:
            assert not p.startswith(nd), f"Pasta ruidosa {nd} não foi podada! Encontrado: {p}"

    assert "legit_src" in rel_paths
    assert "legit_src/app.py" in rel_paths


def test_inspect_directory_negative_depth_resilience(tmp_path: Path) -> None:
    """Verifica que max_depth negativo não causa loop infinito ou crash."""
    repo = tmp_path / "neg_depth_repo"
    repo.mkdir()
    (repo / "test.py").write_text("a = 1\n", encoding="utf-8")

    res = inspect_directory(str(repo), max_depth=-1)
    assert res["status"] == "success"
    assert res["total_files"] == 1


def test_read_code_file_out_of_bounds_and_negative_pagination(tmp_path: Path) -> None:
    """Testa leitura paginada com limites fora de faixa, negativos e invertidos."""
    file_path = tmp_path / "pagination_test.py"
    lines = [f"linha_{i}" for i in range(1, 21)]  # 20 linhas
    file_path.write_text("\n".join(lines), encoding="utf-8")

    # 1. start_line > total_lines -> OUT_OF_BOUNDS
    res_oob = read_code_file(str(file_path), start_line=50, end_line=60)
    assert res_oob["status"] == "error"
    assert res_oob["error"] == "OUT_OF_BOUNDS"

    # 2. start_line negativo, end_line positivo -> ajusta start_line para 1
    res_neg_start = read_code_file(str(file_path), start_line=-5, end_line=3)
    assert res_neg_start["status"] == "success"
    assert res_neg_start["start_line"] == 1
    assert res_neg_start["end_line"] == 3
    assert res_neg_start["lines_returned"] == 3
    assert res_neg_start["lines"][0]["content"] == "linha_1"

    # 3. start_line negativo e end_line menor que 1 -> INVALID_LINE_RANGE
    res_both_neg = read_code_file(str(file_path), start_line=-10, end_line=-1)
    assert res_both_neg["status"] == "error"
    assert res_both_neg["error"] == "INVALID_LINE_RANGE"

    # 4. start_line > end_line -> INVALID_LINE_RANGE
    res_inverted = read_code_file(str(file_path), start_line=15, end_line=10)
    assert res_inverted["status"] == "error"
    assert res_inverted["error"] == "INVALID_LINE_RANGE"

    # 5. end_line maior que total_lines -> ajusta para total_lines (clamp)
    res_clamp = read_code_file(str(file_path), start_line=18, end_line=500)
    assert res_clamp["status"] == "success"
    assert res_clamp["start_line"] == 18
    assert res_clamp["end_line"] == 20
    assert res_clamp["lines_returned"] == 3


def test_read_code_file_binary_detection_null_byte(tmp_path: Path) -> None:
    """Verifica rejeição estrita de arquivos binários contendo null bytes."""
    bin_file = tmp_path / "binary_sample.bin"
    bin_file.write_bytes(b"GIF89a\x00\x00\x00\x01")

    res = read_code_file(str(bin_file), start_line=1, end_line=10)
    assert res["status"] == "error"
    assert res["error"] == "BINARY_FILE"


# ============================================================================
# 4. Testes de Estresse contra Crash com Inputs Anômalos
# ============================================================================


def test_no_unhandled_crashes_on_pathological_inputs(tmp_path: Path) -> None:
    """Submete todas as funções a caminhos e inputs patológicos para garantir zero exceções não tratadas."""
    empty_str = ""
    special_chars = "   \t\n"

    # inspect_directory com espaços em branco e vazio -> erro tratado INVALID_DIRECTORY
    res_dir = inspect_directory(special_chars, max_depth=0)
    assert res_dir["status"] == "error"
    assert res_dir["error"] == "INVALID_DIRECTORY"

    res_dir_empty = inspect_directory(empty_str, max_depth=0)
    assert res_dir_empty["status"] == "error"
    assert res_dir_empty["error"] == "INVALID_DIRECTORY"

    # read_code_file com caminhos anômalos
    res_read = read_code_file(empty_str, start_line=1, end_line=10)
    assert res_read["status"] == "error"
    assert res_read["error"] == "FILE_NOT_FOUND"

    # analyze_ast_anomalies com caminhos anômalos
    res_ast = analyze_ast_anomalies(empty_str)
    assert res_ast["status"] == "error"
    assert res_ast["error"] == "FILE_NOT_FOUND"

    # generate_unified_patch com caminhos anômalos
    res_patch = generate_unified_patch(empty_str, "a", "b")
    assert res_patch["status"] == "error"
    assert res_patch["error"] == "FILE_NOT_FOUND"


# ============================================================================
# 5. Testes de Evidência Empírica de Falhas / Vulnerabilidades Identificadas
# ============================================================================


def test_vulnerability_crlf_mismatch_in_generate_unified_patch(tmp_path: Path) -> None:
    """Verifica se arquivos com quebras de linha Windows CRLF aceitam patches com sucesso após normalização."""
    crlf_file = tmp_path / "crlf_target.py"
    # Arquivo gravado com quebras CRLF típicas do Windows
    crlf_file.write_bytes(b"def processar():\r\n    return 42\r\n")

    # read_code_file normaliza quebras para LF (\n)
    read_res = read_code_file(str(crlf_file), start_line=1, end_line=2)
    assert read_res["status"] == "success"
    read_snippet = read_res["content"]  # 'def processar():\n    return 42'

    # O agente aplica o patch usando exatamente o snippet lido
    patch_res = generate_unified_patch(
        str(crlf_file),
        original_snippet=read_snippet,
        replacement_snippet="def processar():\n    return 84",
    )

    # CORREÇÃO APLICADA: Sucesso na aplicação do patch mesmo com CRLF
    assert patch_res["status"] == "applied"
    assert patch_res["applied"] is True
    assert patch_res["changes_made"] is True


def test_vulnerability_match_case_ast_mccabe_silent_omission(tmp_path: Path) -> None:
    """Verifica se ast.match_case é contado adequadamente na complexidade ciclomática de McCabe."""
    code = """
def route(code):
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Error"
        case _:
            return "Unknown"
"""
    file_path = tmp_path / "match_case_test.py"
    file_path.write_text(code, encoding="utf-8")

    res = analyze_ast_anomalies(str(file_path))
    assert res["status"] == "success"
    # CORREÇÃO APLICADA: mccabe_complexity é 5 (1 base + 4 cases)!
    assert res["functions"][0]["mccabe_complexity"] == 5
