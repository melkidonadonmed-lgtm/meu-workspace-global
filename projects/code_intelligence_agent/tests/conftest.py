"""Fixtures para os testes unitários do Code Intelligence Agent."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_codebase(tmp_path: Path) -> Path:
    """Cria uma estrutura de diretórios e arquivos de exemplo para testes das ferramentas."""
    base_dir = tmp_path / "mock_repo"
    base_dir.mkdir(parents=True, exist_ok=True)

    # 1. Arquivo limpo
    clean_code = '''"""Módulo utilitário simples."""

def somar(a: int, b: int) -> int:
    """Soma dois números."""
    return a + b


def subtrair(a: int, b: int) -> int:
    """Subtrai dois números."""
    return a - b
'''
    (base_dir / "clean_module.py").write_text(clean_code, encoding="utf-8")

    # 2. Arquivo com anomalias propositais:
    # - bare except (BLE001)
    # - except Exception sem noqa
    # - complexidade McCabe > 10 (múltiplos if/elif/for)
    # - função com > 60 linhas físicas
    # - chamada perigosa eval()
    # - argumento padrão mutável (lista)
    anomalies_code = '''"""Módulo com anomalias estruturais e anti-padrões para testes."""
import os

def funcao_complexa(x: int, valores: list = []) -> int:
    """Função com alta complexidade ciclomática e argumento padrão mutável."""
    res = x
    if x > 100:
        res += 10
    elif x > 50:
        res += 5
    elif x > 0:
        res += 1
    elif x < -10:
        res -= 1
    else:
        res += 2

    for i in range(5):
        if i % 2 == 0:
            res += i
        elif i == 3:
            res *= 2
        else:
            res -= 1

    while res < 20:
        if res == 15:
            break
        res += 1

    try:
        resultado_eval = eval("res * 2")
        res = resultado_eval
    except:
        res = 0

    try:
        res += 10
    except Exception:
        res = -1

    return res


def funcao_longa_monolitica() -> None:
    """Função que excede intencionalmente 60 linhas de código."""
    # Linha 1
    # Linha 2
    # Linha 3
    # Linha 4
    # Linha 5
    # Linha 6
    # Linha 7
    # Linha 8
    # Linha 9
    # Linha 10
    # Linha 11
    # Linha 12
    # Linha 13
    # Linha 14
    # Linha 15
    # Linha 16
    # Linha 17
    # Linha 18
    # Linha 19
    # Linha 20
    # Linha 21
    # Linha 22
    # Linha 23
    # Linha 24
    # Linha 25
    # Linha 26
    # Linha 27
    # Linha 28
    # Linha 29
    # Linha 30
    # Linha 31
    # Linha 32
    # Linha 33
    # Linha 34
    # Linha 35
    # Linha 36
    # Linha 37
    # Linha 38
    # Linha 39
    # Linha 40
    # Linha 41
    # Linha 42
    # Linha 43
    # Linha 44
    # Linha 45
    # Linha 46
    # Linha 47
    # Linha 48
    # Linha 49
    # Linha 50
    # Linha 51
    # Linha 52
    # Linha 53
    # Linha 54
    # Linha 55
    # Linha 56
    # Linha 57
    # Linha 58
    # Linha 59
    # Linha 60
    # Linha 61
    print("Linha final da função longa")
'''
    (base_dir / "anomalies_module.py").write_text(anomalies_code, encoding="utf-8")

    # 3. Arquivo com erro de sintaxe
    syntax_broken = '''def func_quebrada(a, b:
    return a + b
'''
    (base_dir / "syntax_error.py").write_text(syntax_broken, encoding="utf-8")

    # 4. Arquivo binário
    (base_dir / "binary.dat").write_bytes(b"\x00\x01\x02\x03\x04\xff")

    # 5. Arquivo de texto comum
    (base_dir / "notes.txt").write_text("Linha 1\nLinha 2\nLinha 3", encoding="utf-8")

    # 6. Arquivo vazio
    (base_dir / "empty.py").write_text("", encoding="utf-8")

    # 7. Subdiretório válido com arquivo
    sub_dir = base_dir / "subpackage"
    sub_dir.mkdir()
    (sub_dir / "sub_module.py").write_text("VAL = 42\n", encoding="utf-8")

    # 8. Pastas que devem ser podadas (pruned)
    git_dir = base_dir / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("dummy git config", encoding="utf-8")

    pycache_dir = base_dir / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "clean_module.cpython-312.pyc").write_bytes(b"pyc")

    venv_dir = base_dir / ".venv"
    venv_dir.mkdir()
    (venv_dir / "lib.py").write_text("dummy venv", encoding="utf-8")

    return base_dir
