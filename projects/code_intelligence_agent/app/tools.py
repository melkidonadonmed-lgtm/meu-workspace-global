"""Ferramentas determinísticas de inteligência de código e análise estática AST."""

import ast
import difflib
import os
import uuid
from pathlib import Path
from typing import Any

# Diretórios que devem ser ignorados para evitar ruído e recursão desnecessária
PRUNE_DIRS: set[str] = {
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
}


def inspect_directory(directory_path: str, max_depth: int) -> dict[str, Any]:
    """Inspeciona a estrutura de um diretório até uma profundidade máxima, podando pastas ruidosas.

    Args:
        directory_path: Caminho do diretório a ser inspecionado.
        max_depth: Profundidade máxima de recursão (0 para apenas o nível atual).

    Returns:
        Dicionário serializável contendo a lista de arquivos/diretórios e métricas estruturais.
    """
    if not directory_path or not directory_path.strip():
        return {
            "status": "error",
            "error": "INVALID_DIRECTORY",
            "message": "O caminho do diretório não pode ser vazio.",
            "directory_path": directory_path,
            "max_depth": max_depth,
            "total_files": 0,
            "total_directories": 0,
            "total_entries": 0,
            "entries": [],
        }

    target_dir = Path(directory_path)
    if not target_dir.exists() or not target_dir.is_dir():
        return {
            "status": "error",
            "error": "DIRECTORY_NOT_FOUND",
            "message": f"O diretório '{directory_path}' não foi encontrado ou não é um diretório válido.",
            "directory_path": directory_path,
            "max_depth": max_depth,
            "total_files": 0,
            "total_directories": 0,
            "total_entries": 0,
            "entries": [],
        }

    base_path = target_dir.resolve()
    entries: list[dict[str, Any]] = []
    total_files = 0
    total_directories = 0

    for root, dirs, files in os.walk(base_path):
        current_path = Path(root)
        rel_to_base = current_path.relative_to(base_path)
        depth = 0 if rel_to_base == Path(".") else len(rel_to_base.parts)

        # Poda diretórios ignorados
        dirs[:] = [d for d in dirs if d not in PRUNE_DIRS and not d.endswith(".egg-info")]

        # Se atingiu a profundidade máxima, não desce nos subdiretórios
        if depth >= max_depth:
            dirs_to_recurse = []
        else:
            dirs_to_recurse = list(dirs)

        # Adiciona diretórios do nível atual aos registros
        for d in sorted(dirs):
            dir_full = current_path / d
            rel_p = dir_full.relative_to(base_path).as_posix()
            entries.append({
                "name": d,
                "path": dir_full.as_posix(),
                "relative_path": rel_p,
                "type": "directory",
                "size_bytes": 0,
                "extension": "",
                "depth": depth + 1,
            })
            total_directories += 1

        # Adiciona arquivos do nível atual aos registros
        for f in sorted(files):
            file_full = current_path / f
            rel_p = file_full.relative_to(base_path).as_posix()
            try:
                size = file_full.stat().st_size
            except OSError:
                size = 0
            entries.append({
                "name": f,
                "path": file_full.as_posix(),
                "relative_path": rel_p,
                "type": "file",
                "size_bytes": size,
                "extension": file_full.suffix,
                "depth": depth + 1,
            })
            total_files += 1

        dirs[:] = dirs_to_recurse

    # Ordena entradas por caminho relativo para garantir determinismo
    entries.sort(key=lambda x: (x["type"] != "directory", x["relative_path"]))

    return {
        "status": "success",
        "directory_path": base_path.as_posix(),
        "max_depth": max_depth,
        "total_files": total_files,
        "total_directories": total_directories,
        "total_entries": len(entries),
        "entries": entries,
    }


def read_code_file(file_path: str, start_line: int, end_line: int) -> dict[str, Any]:
    """Lê um arquivo de código com numeração de linhas 1-indexed e suporte a paginação.

    Args:
        file_path: Caminho do arquivo a ser lido.
        start_line: Linha inicial (1-indexed, inclusive).
        end_line: Linha final (1-indexed, inclusive).

    Returns:
        Dicionário serializável com o conteúdo lido, linhas indexadas e metadados.
    """
    target_file = Path(file_path)
    if not target_file.exists() or not target_file.is_file():
        return {
            "status": "error",
            "error": "FILE_NOT_FOUND",
            "message": f"O arquivo '{file_path}' não foi encontrado ou não é um arquivo válido.",
            "file_path": file_path,
            "total_lines": 0,
            "start_line": start_line,
            "end_line": end_line,
            "lines_returned": 0,
            "content": "",
            "lines": [],
        }

    # Leitura com verificação de arquivo binário e codificações seguras
    try:
        raw_bytes = target_file.read_bytes()
        if b"\x00" in raw_bytes[:1024]:
            return {
                "status": "error",
                "error": "BINARY_FILE",
                "message": f"O arquivo '{file_path}' é binário e não pode ser lido como texto.",
                "file_path": file_path,
                "total_lines": 0,
                "start_line": start_line,
                "end_line": end_line,
                "lines_returned": 0,
                "content": "",
                "lines": [],
            }
        try:
            raw_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = raw_bytes.decode("latin-1")
    except Exception as e:
        return {
            "status": "error",
            "error": "READ_ERROR",
            "message": f"Falha ao ler arquivo '{file_path}': {e}",
            "file_path": file_path,
            "total_lines": 0,
            "start_line": start_line,
            "end_line": end_line,
            "lines_returned": 0,
            "content": "",
            "lines": [],
        }

    raw_lines = raw_text.splitlines()
    total_lines = len(raw_lines)

    if total_lines == 0:
        return {
            "status": "success",
            "file_path": target_file.resolve().as_posix(),
            "total_lines": 0,
            "start_line": start_line,
            "end_line": end_line,
            "lines_returned": 0,
            "content": "",
            "lines": [],
        }

    # Normalização e validação de limites
    eff_start = max(1, start_line)
    if end_line < eff_start:
        return {
            "status": "error",
            "error": "INVALID_LINE_RANGE",
            "message": f"start_line ({start_line}) não pode ser maior que end_line ({end_line}).",
            "file_path": target_file.resolve().as_posix(),
            "total_lines": total_lines,
            "start_line": start_line,
            "end_line": end_line,
            "lines_returned": 0,
            "content": "",
            "lines": [],
        }

    if eff_start > total_lines:
        return {
            "status": "error",
            "error": "OUT_OF_BOUNDS",
            "message": f"start_line ({start_line}) excede o total de linhas do arquivo ({total_lines}).",
            "file_path": target_file.resolve().as_posix(),
            "total_lines": total_lines,
            "start_line": start_line,
            "end_line": end_line,
            "lines_returned": 0,
            "content": "",
            "lines": [],
        }

    eff_end = min(total_lines, end_line)
    selected_raw = raw_lines[eff_start - 1 : eff_end]

    line_items = [
        {"line_number": eff_start + i, "content": line}
        for i, line in enumerate(selected_raw)
    ]
    content = "\n".join(selected_raw)

    return {
        "status": "success",
        "file_path": target_file.resolve().as_posix(),
        "total_lines": total_lines,
        "start_line": eff_start,
        "end_line": eff_end,
        "lines_returned": len(line_items),
        "content": content,
        "lines": line_items,
    }


def _count_decisions(node: ast.AST) -> int:
    """Calcula recursivamente os pontos de decisão McCabe de um nó AST sem invadir funções aninhadas."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return 0
    count = 0
    if isinstance(node, (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.ExceptHandler,
        ast.IfExp,
        ast.Assert,
    )):
        count += 1
    elif isinstance(node, ast.BoolOp):
        count += max(0, len(node.values) - 1)
    elif (
        (hasattr(ast, "match_case") and isinstance(node, getattr(ast, "match_case")))
        or (hasattr(ast, "MatchCase") and isinstance(node, getattr(ast, "MatchCase")))
    ):
        count += 1

    for child in ast.iter_child_nodes(node):
        count += _count_decisions(child)
    return count


def _calculate_mccabe_complexity(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Calcula a complexidade ciclomática de McCabe (1 + pontos de decisão)."""
    complexity = 1
    for child in ast.iter_child_nodes(func_node):
        complexity += _count_decisions(child)
    return complexity


def analyze_ast_anomalies(file_path: str) -> dict[str, Any]:
    """Realiza análise estática avançada na AST do Python detectando sintaxe, BLE001, McCabe e smells.

    Args:
        file_path: Caminho do arquivo Python (.py) para análise estática.

    Returns:
        Dicionário serializável com anomalias detectadas, complexidade McCabe e métricas estruturais.
    """
    target_file = Path(file_path)
    if not target_file.exists() or not target_file.is_file():
        return {
            "status": "error",
            "error": "FILE_NOT_FOUND",
            "message": f"O arquivo '{file_path}' não foi encontrado ou não é um arquivo válido.",
            "file_path": file_path,
            "is_valid_syntax": False,
            "syntax_error": None,
            "anomalies": [],
            "functions": [],
            "classes": [],
            "metrics": {
                "total_anomalies": 0,
                "max_mccabe_complexity": 0,
                "total_functions": 0,
                "total_classes": 0,
            },
        }

    if target_file.suffix.lower() != ".py":
        return {
            "status": "error",
            "error": "NOT_PYTHON_FILE",
            "message": f"O arquivo '{file_path}' não é um arquivo Python (.py). A análise de AST suporta apenas Python.",
            "file_path": target_file.resolve().as_posix(),
            "is_valid_syntax": False,
            "syntax_error": None,
            "anomalies": [],
            "functions": [],
            "classes": [],
            "metrics": {
                "total_anomalies": 0,
                "max_mccabe_complexity": 0,
                "total_functions": 0,
                "total_classes": 0,
            },
        }

    try:
        raw_bytes = target_file.read_bytes()
        try:
            source_code = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            source_code = raw_bytes.decode("latin-1")
    except Exception as e:
        return {
            "status": "error",
            "error": "READ_ERROR",
            "message": f"Falha ao ler o arquivo '{file_path}': {e}",
            "file_path": target_file.resolve().as_posix(),
            "is_valid_syntax": False,
            "syntax_error": None,
            "anomalies": [],
            "functions": [],
            "classes": [],
            "metrics": {
                "total_anomalies": 0,
                "max_mccabe_complexity": 0,
                "total_functions": 0,
                "total_classes": 0,
            },
        }

    source_lines = source_code.splitlines()

    # 1. Validação de Sintaxe
    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        syntax_err = {
            "line": e.lineno or 0,
            "column": e.offset or 0,
            "message": e.msg,
            "text": (e.text or "").strip(),
        }
        return {
            "status": "syntax_error",
            "file_path": target_file.resolve().as_posix(),
            "is_valid_syntax": False,
            "syntax_error": syntax_err,
            "anomalies": [
                {
                    "type": "syntax_error",
                    "severity": "critical",
                    "rule": "SYNTAX",
                    "line": e.lineno or 0,
                    "column": e.offset or 0,
                    "message": f"Erro de sintaxe: {e.msg}",
                }
            ],
            "functions": [],
            "classes": [],
            "metrics": {
                "total_anomalies": 1,
                "max_mccabe_complexity": 0,
                "total_functions": 0,
                "total_classes": 0,
            },
        }

    anomalies: list[dict[str, Any]] = []
    functions_meta: list[dict[str, Any]] = []
    classes_meta: list[dict[str, Any]] = []
    max_mccabe = 1

    # 2. Detecção de Bare Except e Generic Except (BLE001)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            lineno = getattr(node, "lineno", 0)
            src_line = source_lines[lineno - 1] if 1 <= lineno <= len(source_lines) else ""
            is_suppressed = "noqa: BLE001" in src_line or "noqa: bare-except" in src_line

            if node.type is None:
                # except: sem tipo
                anomalies.append({
                    "type": "bare_except",
                    "severity": "high",
                    "rule": "BLE001",
                    "line": lineno,
                    "message": "Cláusula 'except:' sem tipo especificado captura BaseException indevidamente.",
                    "suppressed": is_suppressed,
                })
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                if not is_suppressed:
                    anomalies.append({
                        "type": "generic_except",
                        "severity": "warning",
                        "rule": "BLE001",
                        "line": lineno,
                        "message": "Captura genérica 'except Exception' sem comentário de supressão (# noqa: BLE001).",
                        "suppressed": False,
                    })

    # 3. Análise de Funções (McCabe Complexity, Funções Longas > 60 linhas e Argumentos Mutáveis)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn_name = node.name
            lineno = node.lineno
            end_lineno = getattr(node, "end_lineno", lineno)
            func_lines = end_lineno - lineno + 1

            complexity = _calculate_mccabe_complexity(node)
            if complexity > max_mccabe:
                max_mccabe = complexity

            functions_meta.append({
                "name": fn_name,
                "line": lineno,
                "end_line": end_lineno,
                "lines_count": func_lines,
                "mccabe_complexity": complexity,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            })

            # Complexidade excessiva > 10
            if complexity > 10:
                anomalies.append({
                    "type": "high_complexity",
                    "severity": "warning",
                    "rule": "MCCABE",
                    "line": lineno,
                    "function_name": fn_name,
                    "complexity": complexity,
                    "message": f"Função '{fn_name}' possui complexidade ciclomática de {complexity} (> 10). Recomendada refatoração.",
                })

            # Função monolítica > 60 linhas físicas
            if func_lines > 60:
                anomalies.append({
                    "type": "long_function",
                    "severity": "info",
                    "rule": "FUNCTION_LENGTH",
                    "line": lineno,
                    "function_name": fn_name,
                    "lines_count": func_lines,
                    "message": f"Função '{fn_name}' possui {func_lines} linhas físicas (> 60 linhas). Recomendada modularização.",
                })

            # Argumentos padrão mutáveis (list, dict, set)
            all_defaults = [d for d in node.args.defaults if d is not None] + [
                d for d in node.args.kw_defaults if d is not None
            ]
            for default in all_defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    anomalies.append({
                        "type": "mutable_default_arg",
                        "severity": "warning",
                        "rule": "MUTABLE_DEFAULT",
                        "line": getattr(default, "lineno", lineno),
                        "function_name": fn_name,
                        "message": f"Argumento padrão mutável detectado na função '{fn_name}'. Prefira None com inicialização interna.",
                    })

    # 4. Detecção de Classes
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            cls_name = node.name
            lineno = node.lineno
            end_lineno = getattr(node, "end_lineno", lineno)
            methods = [
                m.name
                for m in node.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes_meta.append({
                "name": cls_name,
                "line": lineno,
                "end_line": end_lineno,
                "methods": methods,
            })

    # 5. Chamadas Perigosas (eval, exec, __import__, os.system)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = ""
            if isinstance(node.func, ast.Name):
                call_name = node.func.id
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                call_name = f"{node.func.value.id}.{node.func.attr}"

            if call_name in {"eval", "exec", "__import__", "os.system"}:
                anomalies.append({
                    "type": "dangerous_call",
                    "severity": "high",
                    "rule": "SECURITY",
                    "line": getattr(node, "lineno", 0),
                    "call": call_name,
                    "message": f"Chamada à função potencialmente perigosa '{call_name}()' detectada.",
                })

    # Ordena anomalias por linha para previsibilidade
    anomalies.sort(key=lambda a: a.get("line", 0))

    return {
        "status": "success",
        "file_path": target_file.resolve().as_posix(),
        "is_valid_syntax": True,
        "syntax_error": None,
        "anomalies": anomalies,
        "functions": functions_meta,
        "classes": classes_meta,
        "metrics": {
            "total_anomalies": len(anomalies),
            "max_mccabe_complexity": max_mccabe,
            "total_functions": len(functions_meta),
            "total_classes": len(classes_meta),
        },
    }


def generate_unified_patch(
    file_path: str, original_snippet: str, replacement_snippet: str
) -> dict[str, Any]:
    """Gera e aplica um patch unified diff com validação sintática AST obrigatória em dry-run antes da gravação.

    Args:
        file_path: Caminho do arquivo a ser modificado.
        original_snippet: Trecho original exato que será substituído.
        replacement_snippet: Novo trecho substituto.

    Returns:
        Dicionário serializável informando status ('applied' ou 'rejected'), diff gerado e detalhes da validação.
    """
    target_file = Path(file_path)
    if not target_file.exists() or not target_file.is_file():
        return {
            "status": "error",
            "applied": False,
            "error": "FILE_NOT_FOUND",
            "message": f"Arquivo '{file_path}' não foi encontrado ou não é um arquivo válido.",
            "file_path": file_path,
            "diff": "",
            "changes_made": False,
        }

    # Leitura do conteúdo original
    try:
        raw_bytes = target_file.read_bytes()
        try:
            original_content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            original_content = raw_bytes.decode("latin-1")
    except Exception as e:
        return {
            "status": "error",
            "applied": False,
            "error": "READ_ERROR",
            "message": f"Falha ao ler arquivo '{file_path}': {e}",
            "file_path": target_file.resolve().as_posix(),
            "diff": "",
            "changes_made": False,
        }

    # Normalização de quebras de linha (\r\n -> \n) para compatibilidade perfeita no Windows
    original_content = original_content.replace("\r\n", "\n")
    norm_original_snippet = original_snippet.replace("\r\n", "\n")
    norm_replacement_snippet = replacement_snippet.replace("\r\n", "\n")

    # Validação de correspondência exata e unicidade do trecho alvo
    occurrences = original_content.count(norm_original_snippet)
    if occurrences == 0:
        return {
            "status": "error",
            "applied": False,
            "error": "TARGET_NOT_FOUND",
            "message": f"O trecho alvo original não foi encontrado no arquivo '{file_path}'.",
            "file_path": target_file.resolve().as_posix(),
            "diff": "",
            "changes_made": False,
        }

    if occurrences > 1:
        return {
            "status": "error",
            "applied": False,
            "error": "AMBIGUOUS_MATCH",
            "message": (
                f"O trecho alvo foi encontrado {occurrences} vezes no arquivo '{file_path}'. "
                "Forneça um trecho de contexto mais abrangente para garantir unicidade."
            ),
            "file_path": target_file.resolve().as_posix(),
            "diff": "",
            "changes_made": False,
        }

    # Gera o conteúdo substituto em memória (dry-run)
    new_content = original_content.replace(norm_original_snippet, norm_replacement_snippet, 1)

    if new_content == original_content:
        return {
            "status": "no_op",
            "applied": False,
            "message": "O trecho de substituição é idêntico ao original. Nenhuma alteração realizada.",
            "file_path": target_file.resolve().as_posix(),
            "diff": "",
            "changes_made": False,
        }

    # Gera o unified diff
    orig_lines = original_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff_generator = difflib.unified_diff(
        orig_lines,
        new_lines,
        fromfile=f"a/{target_file.name}",
        tofile=f"b/{target_file.name}",
    )
    diff_text = "".join(diff_generator)

    # VALIDAÇÃO AST EM DRY-RUN: Se for arquivo Python, verifica integridade sintática ANTES da gravação
    if target_file.suffix.lower() == ".py":
        try:
            ast.parse(new_content, filename=file_path)
        except SyntaxError as e:
            return {
                "status": "rejected",
                "applied": False,
                "error": "SYNTAX_ERROR",
                "message": (
                    f"Patch REJEITADO por violação de integridade sintática AST: {e.msg} na linha {e.lineno}."
                ),
                "syntax_error": {
                    "line": e.lineno or 0,
                    "column": e.offset or 0,
                    "message": e.msg,
                    "text": (e.text or "").strip(),
                },
                "file_path": target_file.resolve().as_posix(),
                "diff": diff_text,
                "changes_made": False,
            }

    # Gravação atômica segura no disco com identificador único
    temp_file = target_file.with_name(f"{target_file.name}.tmp_{os.getpid()}_{uuid.uuid4().hex[:8]}")
    try:
        temp_file.write_text(new_content, encoding="utf-8", newline="\n")
        temp_file.replace(target_file)
    except Exception as e:
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)
        return {
            "status": "error",
            "applied": False,
            "error": "WRITE_ERROR",
            "message": f"Erro durante a gravação atômica do arquivo '{file_path}': {e}",
            "file_path": target_file.resolve().as_posix(),
            "diff": diff_text,
            "changes_made": False,
        }

    return {
        "status": "applied",
        "applied": True,
        "file_path": target_file.resolve().as_posix(),
        "diff": diff_text,
        "changes_made": True,
        "message": "Patch aplicado com sucesso após validação sintática AST prévia.",
    }
