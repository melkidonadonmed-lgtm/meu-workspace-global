"""Interface de Linha de Comando (CLI) para o Code Intelligence Agent (R4).

Comandos disponíveis via entrypoint 'code-intel':
- code-intel run "<prompt>": executa instrução com o agente e guardrails de segurança.
- code-intel inspect <path>: realiza varredura e diagnóstico AST de arquivo ou pasta.
- code-intel serve [--port 8000]: inicia o servidor REST FastAPI com uvicorn.
- code-intel eval: dispara a suíte de avaliação automatizada Quality Flywheel.
"""

from pathlib import Path
from typing import Optional

import typer

from app.guardrails import (
    is_destructive_command,
    redact_sensitive_info,
    validate_path_boundary,
)
from app.tools import (
    analyze_ast_anomalies,
    inspect_directory,
    read_code_file,
)

cli_app = typer.Typer(
    name="code-intel",
    help="Code Intelligence & Tool Calling Agent CLI (Google ADK & Antigravity)",
    add_completion=False,
)


@cli_app.command("run")
def run_command(
    prompt: str = typer.Argument(..., help="Instrução ou comando a ser executado pelo agente"),
    session_id: Optional[str] = typer.Option(
        None, "--session-id", "-s", help="Identificador único da sessão"
    ),
    workspace: Optional[str] = typer.Option(
        None, "--workspace", "-w", help="Diretório raiz de trabalho"
    ),
) -> None:
    """Executa uma instrução com o agente, aplicando guardrails e histórico de ferramentas."""
    workspace_path = workspace or Path.cwd().as_posix()
    typer.echo(f"[*] Executando Code Intelligence Agent [Workspace: {workspace_path}]")
    typer.echo(f"[*] Prompt: {prompt}\n")

    # 1. Guardrail de comandos destrutivos
    is_dest, reason = is_destructive_command(prompt)
    if is_dest:
        typer.secho(
            f"[VIOLAÇÃO DE SEGURANÇA] {reason}\nA operação foi interceptada e cancelada.",
            fg=typer.colors.RED,
            bold=True,
        )
        raise typer.Exit(code=1)

    prompt_lower = prompt.lower()
    tools_executed: list[str] = []

    # 2. Despacho e resolução de intenção
    if "inspect" in prompt_lower or "diretorio" in prompt_lower or "diretório" in prompt_lower:
        dir_res = inspect_directory(workspace_path, max_depth=1)
        tools_executed.append("inspect_directory")
        typer.secho("[FERRAMENTA] inspect_directory executada:", fg=typer.colors.CYAN)
        typer.echo(
            f"  - Total de arquivos: {dir_res.get('total_files', 0)}\n"
            f"  - Total de diretórios: {dir_res.get('total_directories', 0)}"
        )
    elif "analyze" in prompt_lower or "ast" in prompt_lower or "anomalia" in prompt_lower:
        words = prompt.split()
        target = None
        for w in words:
            cleaned = w.strip("\"'`,;:()")
            if cleaned.endswith(".py"):
                target = cleaned
                break
        if target:
            allowed, b_reason = validate_path_boundary(target, workspace_path)
            if not allowed:
                typer.secho(f"[BLOQUEIO DE FRONTEIRA] {b_reason}", fg=typer.colors.RED, bold=True)
                raise typer.Exit(code=1)
            ast_res = analyze_ast_anomalies(target)
            tools_executed.append("analyze_ast_anomalies")
            typer.secho(f"[FERRAMENTA] analyze_ast_anomalies em '{target}':", fg=typer.colors.CYAN)
            typer.echo(f"  - Linhas: {ast_res.get('total_lines', 0)}")
            typer.echo(f"  - Anomalias: {ast_res.get('total_anomalies', 0)}")
            for anom in ast_res.get("anomalies", []):
                typer.secho(f"    * Linha {anom.get('line')}: [{anom.get('type')}] {anom.get('message')}", fg=typer.colors.YELLOW)
        else:
            typer.echo("Instrução de análise reconhecida. Forneça o arquivo Python alvo.")
    elif "read" in prompt_lower or "ler" in prompt_lower:
        words = prompt.split()
        target = None
        for w in words:
            cleaned = w.strip("\"'`,;:()")
            if "." in cleaned and "/" in cleaned or cleaned.endswith(".py") or cleaned.endswith(".json") or cleaned.endswith(".md"):
                target = cleaned
                break
        if target:
            allowed, b_reason = validate_path_boundary(target, workspace_path)
            if not allowed:
                typer.secho(f"[BLOQUEIO DE FRONTEIRA] {b_reason}", fg=typer.colors.RED, bold=True)
                raise typer.Exit(code=1)
            read_res = read_code_file(target, start_line=1, end_line=50)
            tools_executed.append("read_code_file")
            content_safe = redact_sensitive_info(read_res.get("content", ""))
            typer.secho(f"[FERRAMENTA] read_code_file em '{target}':", fg=typer.colors.CYAN)
            typer.echo(f"  - Linhas lidas: {read_res.get('total_lines_read', 0)}")
            typer.echo(f"  - Conteúdo:\n{content_safe[:300]}")
    else:
        typer.secho("[INFO] Instrução interpretada com sucesso sem necessidade de mutações.", fg=typer.colors.GREEN)

    typer.secho(f"\n[SUCESSO] Pipeline concluído com segurança. Ferramentas disparadas: {tools_executed or 'Nenhuma'}", fg=typer.colors.GREEN)


@cli_app.command("inspect")
def inspect_command(
    path: str = typer.Argument(..., help="Caminho do arquivo Python ou diretório a inspecionar"),
    max_depth: int = typer.Option(2, "--max-depth", "-d", help="Profundidade máxima de varredura para diretórios"),
    workspace_root: Optional[str] = typer.Option(
        None, "--workspace-root", "-w", help="Raiz de confinamento permitida"
    ),
) -> None:
    """Inspeciona e analisa a AST de um arquivo Python ou estrutura de pastas."""
    target_path = Path(path)

    # 1. Validação de fronteira (se workspace_root for fornecido explicitamente)
    if workspace_root is not None:
        allowed, b_reason = validate_path_boundary(path, workspace_root)
        if not allowed:
            typer.secho(f"[ACESSO NEGADO] {b_reason}", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)

    if not target_path.exists():
        typer.secho(f"[ERRO] O alvo '{path}' não existe no filesystem.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # 2. Análise de arquivo Python
    if target_path.is_file():
        if target_path.suffix.lower() != ".py":
            typer.secho(f"[AVISO] O arquivo '{path}' não é um script Python (.py).", fg=typer.colors.YELLOW)

        res = analyze_ast_anomalies(path)
        if res.get("status") == "error":
            typer.secho(f"[ERRO] Falha na análise AST: {res.get('message')}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        typer.secho(f"\n=== Diagnóstico AST: {path} ===", fg=typer.colors.BLUE, bold=True)
        typer.echo(f"Status: {res.get('status')}")
        typer.echo(f"Sintaxe Válida: {res.get('is_valid_syntax', res.get('syntax_valid', True))}")
        metrics = res.get("metrics", {})
        typer.echo(f"Score de Complexidade: {metrics.get('max_mccabe_complexity', 0)}")
        typer.echo(f"Funções Detectadas: {len(res.get('functions', []))}")
        typer.echo(f"Classes Detectadas: {len(res.get('classes', []))}")

        anomalies = res.get("anomalies", [])
        total_anom = metrics.get("total_anomalies", len(anomalies))
        if total_anom == 0:
            typer.secho("\n[OK] Nenhuma anomalia de código ou sintaxe identificada.", fg=typer.colors.GREEN)
        else:
            typer.secho(f"\n[ALERTA] {total_anom} anomalia(s) encontrada(s):", fg=typer.colors.YELLOW, bold=True)
            for anom in anomalies:
                typer.echo(f"  - [Linha {anom.get('line')}] ({anom.get('type')}): {anom.get('message')}")

    # 3. Análise de diretório
    elif target_path.is_dir():
        typer.secho(f"\n=== Inspeção de Diretório: {path} ===", fg=typer.colors.BLUE, bold=True)
        dir_res = inspect_directory(path, max_depth)
        typer.echo(f"Arquivos: {dir_res.get('total_files')}")
        typer.echo(f"Diretórios: {dir_res.get('total_directories')}")
        typer.echo(f"Total de Entradas: {dir_res.get('total_entries')}")

        py_files = [e for e in dir_res.get("entries", []) if e.get("path", "").endswith(".py")]
        typer.echo(f"Arquivos Python (.py): {len(py_files)}")
        if py_files:
            typer.secho("\nArquivos Python catalogados:", fg=typer.colors.CYAN)
            for pf in py_files[:10]:
                typer.echo(f"  * {pf.get('path')} ({pf.get('size_bytes')} bytes)")


@cli_app.command("serve")
def serve_command(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host de binding do servidor"),
    port: int = typer.Option(8000, "--port", "-p", help="Porta HTTP de escuta"),
    reload: bool = typer.Option(False, "--reload", help="Habilitar hot-reload para desenvolvimento"),
) -> None:
    """Inicia o servidor FastAPI do Code Intelligence Agent com uvicorn."""
    import uvicorn

    typer.secho(f"[*] Iniciando Code Intelligence Agent API em http://{host}:{port}", fg=typer.colors.GREEN)
    uvicorn.run("app.fast_api_app:fastapi_app", host=host, port=port, reload=reload)


@cli_app.command("eval")
def eval_command(
    config: str = typer.Option(
        "tests/eval/eval_config.yaml", "--config", "-c", help="Caminho do arquivo de configuração"
    ),
    dataset: str = typer.Option(
        "tests/eval/datasets/code_intelligence_multi_turn.json",
        "--dataset",
        "-d",
        help="Caminho do dataset multi-turn",
    ),
    artifacts_dir: str = typer.Option(
        "artifacts/grade_results", "--artifacts-dir", "-a", help="Diretório para saída dos relatórios"
    ),
) -> None:
    """Executa a suíte de avaliação automatizada Quality Flywheel."""
    from tests.eval.eval_runner import CodeIntelligenceEvalRunner

    # Resolução dinâmica de caminhos (relativo ao projeto caso executado de outro CWD)
    project_root = Path(__file__).resolve().parent.parent
    c_path = Path(config)
    if not c_path.exists() and (project_root / config).exists():
        c_path = project_root / config

    d_path = Path(dataset)
    if not d_path.exists() and (project_root / dataset).exists():
        d_path = project_root / dataset

    a_path = Path(artifacts_dir)
    if not a_path.is_absolute() and not a_path.exists():
        a_path = project_root / artifacts_dir

    typer.secho("[*] Disparando Quality Flywheel Evaluation Runner...", fg=typer.colors.CYAN, bold=True)
    runner = CodeIntelligenceEvalRunner(
        config_path=str(c_path),
        dataset_path=str(d_path),
        artifacts_dir=str(a_path),
    )
    result = runner.run_evaluation()

    if result.get("passed"):
        typer.secho("\n[PASS] Quality Flywheel: Todos os critérios e thresholds foram atingidos!", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"  - multi_turn_task_success: {result['metrics']['multi_turn_task_success']:.2%}")
        typer.echo(f"  - multi_turn_tool_use_quality: {result['metrics']['multi_turn_tool_use_quality']:.2%}")
        typer.echo(f"  - security_guardrail_compliance: {result['metrics']['security_guardrail_compliance']:.2%}")
        typer.echo(f"\nRelatório JSON: {result.get('json_report')}")
        typer.echo(f"Relatório HTML: {result.get('html_report')}")
    else:
        typer.secho("\n[FAIL] Quality Flywheel: Thresholds não atingidos.", fg=typer.colors.RED, bold=True)
        typer.echo(f"Métricas: {result.get('metrics')}")
        raise typer.Exit(code=1)


def main() -> None:
    """Entrypoint principal da linha de comando."""
    cli_app()


if __name__ == "__main__":
    main()
