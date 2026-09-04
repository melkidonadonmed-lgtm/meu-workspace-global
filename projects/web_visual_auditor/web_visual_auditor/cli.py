"""Interface de Linha de Comando (CLI) para o Web Visual Auditor.

Fornece uma interface unificada via argparse com 5 subcomandos canônicos:
1. `search`: Pesquisa web estruturada e higienização semântica de fontes.
2. `dom-inspect`: Inspeção estrutural e geométrica do DOM (coordenadas e visibilidade).
3. `visual-diff`: Regressão visual diferencial pixel a pixel entre duas imagens.
4. `component-diff`: Auditoria granular e isolada por micro-componentes de design system.
5. `suite`: Execução orquestrada de ponta a ponta gerando relatórios consolidados.

Códigos de saída POSIX padronizados:
- 0: Sucesso absoluto e sem divergência visual detectada.
- 1: Divergência visual detectada (regressão) OU erro de execução/exceção.
- 2: Erro de sintaxe nos argumentos de linha de comando.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from web_visual_auditor.exceptions import AuditorError
from web_visual_auditor.suite import SuiteConfig, WebVisualAuditorSuite

logger = logging.getLogger(__name__)


def _parse_selectors(raw: str | list[str] | None) -> list[str]:
    """Normaliza seletores CSS a partir de string separada por vírgula ou lista."""
    if not raw:
        return []
    if isinstance(raw, list):
        items: list[str] = []
        for entry in raw:
            items.extend([s.strip() for s in entry.split(",") if s.strip()])
        return items
    return [s.strip() for s in raw.split(",") if s.strip()]


def _emit_output(content: str, output_file: str | None = None) -> None:
    """Emite o conteúdo na saída padrão e opcionalmente em arquivo."""
    print(content)
    if output_file:
        out_p = Path(output_file)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Constrói a árvore de subcomandos e argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="web-visual-auditor",
        description="Web Visual Auditor - Suíte de pesquisa semântica, inspeção DOM e regressão visual.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        title="Subcomandos disponíveis",
        dest="subcommand",
        metavar="<comando>",
    )

    # -------------------------------------------------------------------------
    # 1. Subcomando: search
    # -------------------------------------------------------------------------
    search_p = subparsers.add_parser(
        "search",
        help="Executa pesquisa web semântica e normaliza referências de conteúdo.",
        description="Consulta fontes web, elimina tags ruidosas e retorna referências estruturadas.",
    )
    search_p.add_argument(
        "query",
        nargs="?",
        default="",
        help="Termo ou query de busca semântica.",
    )
    search_p.add_argument(
        "-q",
        "--query",
        dest="query_flag",
        default=None,
        help="Query alternativa via flag.",
    )
    search_p.add_argument(
        "-l",
        "--limit",
        "--max-results",
        dest="limit",
        type=int,
        default=5,
        help="Limite máximo de artigos e fontes a recuperar.",
    )
    search_p.add_argument(
        "--offline",
        action="store_true",
        help="Força a execução em modo determinístico offline.",
    )
    search_p.add_argument(
        "--json",
        action="store_true",
        help="Formata e imprime a saída no formato JSON.",
    )
    search_p.add_argument(
        "-o",
        "--output",
        dest="output",
        default=None,
        help="Caminho opcional para salvar o resultado em arquivo.",
    )

    # -------------------------------------------------------------------------
    # 2. Subcomando: dom-inspect
    # -------------------------------------------------------------------------
    dom_p = subparsers.add_parser(
        "dom-inspect",
        help="Inspeciona nós do DOM e computa geometrias (getBoundingClientRect) e visibilidade.",
        description="Renderiza URL web, arquivo local ou HTML e extrai coordenadas precisas dos elementos.",
    )
    dom_p.add_argument(
        "target",
        nargs="?",
        default="",
        help="URL, caminho de arquivo local ou marcação HTML a ser inspecionada.",
    )
    dom_p.add_argument(
        "-u",
        "--url",
        dest="url_flag",
        default=None,
        help="URL ou caminho de arquivo alternativo via flag.",
    )
    dom_p.add_argument(
        "--html",
        dest="html_flag",
        default=None,
        help="Conteúdo HTML direto via flag.",
    )
    dom_p.add_argument(
        "-s",
        "--selectors",
        dest="selectors",
        default=None,
        help="Seletores CSS específicos separados por vírgula (ex: header,nav,button,h1).",
    )
    dom_p.add_argument(
        "--json",
        action="store_true",
        help="Formata e imprime a saída no formato JSON.",
    )
    dom_p.add_argument(
        "-o",
        "--output",
        dest="output",
        default=None,
        help="Caminho opcional para salvar o resultado em arquivo.",
    )

    # -------------------------------------------------------------------------
    # 3. Subcomando: visual-diff
    # -------------------------------------------------------------------------
    diff_p = subparsers.add_parser(
        "visual-diff",
        help="Executa regressão visual diferencial pixel a pixel entre duas imagens.",
        description="Compara imagens com tolerância a antialiasing (canal > 15) e gera máscara vermelha (#FF0000).",
    )
    diff_p.add_argument(
        "-b",
        "--baseline",
        dest="baseline",
        required=True,
        help="Caminho do arquivo de imagem base (referência).",
    )
    diff_p.add_argument(
        "-c",
        "--current",
        dest="current",
        required=True,
        help="Caminho do arquivo de imagem atual sob auditoria.",
    )
    diff_p.add_argument(
        "-d",
        "--diff-out",
        dest="diff_out",
        default="diff_result.png",
        help="Caminho para gravação da máscara visual diferencial (#FF0000).",
    )
    diff_p.add_argument(
        "-t",
        "--tolerance",
        dest="tolerance",
        type=int,
        default=15,
        help="Limiar de tolerância por canal RGB contra antialiasing (0 a 255).",
    )
    diff_p.add_argument(
        "--json",
        action="store_true",
        help="Formata e imprime a saída no formato JSON.",
    )
    diff_p.add_argument(
        "-o",
        "--output",
        dest="output",
        default=None,
        help="Caminho opcional para salvar o resumo em arquivo.",
    )

    # -------------------------------------------------------------------------
    # 4. Subcomando: component-diff
    # -------------------------------------------------------------------------
    comp_p = subparsers.add_parser(
        "component-diff",
        help="Audita micro-componentes isolados por seletores CSS de design system.",
        description="Recorta e compara seletores independentemente entre duas versões de página.",
    )
    comp_p.add_argument(
        "-b",
        "--baseline",
        "--baseline-url",
        dest="baseline",
        required=True,
        help="URL ou caminho da página baseline.",
    )
    comp_p.add_argument(
        "-c",
        "--current",
        "--current-url",
        dest="current",
        required=True,
        help="URL ou caminho da página atual sob auditoria.",
    )
    comp_p.add_argument(
        "-s",
        "--selectors",
        dest="selectors",
        required=True,
        help="Seletores CSS a isolar e comparar (separados por vírgula).",
    )
    comp_p.add_argument(
        "--diff-dir",
        "--output-dir",
        dest="diff_dir",
        default="component_diffs",
        help="Diretório onde snapshots recortados e máscaras diferenciais serão gravados.",
    )
    comp_p.add_argument(
        "-t",
        "--tolerance",
        dest="tolerance",
        type=int,
        default=15,
        help="Limiar de tolerância de antialiasing por canal.",
    )
    comp_p.add_argument(
        "--json",
        action="store_true",
        help="Formata e imprime a saída no formato JSON.",
    )
    comp_p.add_argument(
        "-o",
        "--output",
        dest="output",
        default=None,
        help="Caminho opcional para salvar o relatório de componentes em arquivo.",
    )

    # -------------------------------------------------------------------------
    # 5. Subcomando: suite
    # -------------------------------------------------------------------------
    suite_p = subparsers.add_parser(
        "suite",
        help="Executa a suíte de auditoria completa de ponta a ponta.",
        description="Orquestra pesquisa semântica, inspeção DOM, diff fullpage e micro-componentes.",
    )
    suite_p.add_argument(
        "-b",
        "--baseline",
        "--baseline-url",
        dest="baseline",
        required=True,
        help="URL, caminho ou imagem de baseline.",
    )
    suite_p.add_argument(
        "-c",
        "--current",
        "--current-url",
        dest="current",
        required=True,
        help="URL, caminho ou imagem sob auditoria.",
    )
    suite_p.add_argument(
        "-s",
        "--selectors",
        dest="selectors",
        default=None,
        help="Seletores CSS de micro-componentes para isolamento (separados por vírgula).",
    )
    suite_p.add_argument(
        "-q",
        "--query",
        dest="query",
        default=None,
        help="Termo de pesquisa semântica opcional para contextualização.",
    )
    suite_p.add_argument(
        "-t",
        "--tolerance",
        dest="tolerance",
        type=int,
        default=15,
        help="Limiar de tolerância de canal RGB.",
    )
    suite_p.add_argument(
        "--output-dir",
        dest="output_dir",
        default="audit_reports",
        help="Diretório de saída para todos os artefatos gerados pela suíte.",
    )
    suite_p.add_argument(
        "--diff-out",
        dest="diff_out",
        default="diff_result.png",
        help="Nome da máscara diferencial fullpage.",
    )
    suite_p.add_argument(
        "--json",
        action="store_true",
        help="Formata e imprime o relatório completo em JSON.",
    )
    suite_p.add_argument(
        "-o",
        "--output",
        dest="output",
        default=None,
        help="Arquivo opcional para persistir o relatório consolidado.",
    )

    return parser


# =============================================================================
# Handlers de Cada Subcomando
# =============================================================================


def _handle_search(args: argparse.Namespace, suite: WebVisualAuditorSuite) -> int:
    """Manipula a execução do subcomando 'search'."""
    query = args.query_flag or args.query
    if not query or not query.strip():
        sys.stderr.write("Erro: É necessário informar uma query de pesquisa.\n")
        return 1

    refs = suite.run_semantic_research(query=query.strip(), limit=args.limit)

    if args.json:
        payload = [ref.model_dump(mode="json") for ref in refs]
        _emit_output(json.dumps(payload, indent=2, ensure_ascii=False), args.output)
        return 0

    # Saída amigável em texto
    lines: list[str] = [
        f"=== Pesquisa Semântica: '{query}' (Resultados: {len(refs)}) ==="
    ]
    for i, ref in enumerate(refs, 1):
        lines.append(f"[{i}] {ref.title}")
        lines.append(f"    URL: {ref.url}")
        lines.append(f"    Snippet: {ref.snippet[:120]}...")
        lines.append("")

    _emit_output("\n".join(lines).strip(), args.output)
    return 0


def _handle_dom_inspect(args: argparse.Namespace, suite: WebVisualAuditorSuite) -> int:
    """Manipula a execução do subcomando 'dom-inspect'."""
    target = args.html_flag or args.url_flag or args.target
    if not target or not target.strip():
        sys.stderr.write("Erro: É necessário fornecer uma URL, arquivo ou marcação HTML.\n")
        return 1

    selectors = _parse_selectors(args.selectors)
    nodes = suite.run_dom_audit(
        url_or_html=target.strip(),
        selectors=selectors if selectors else None,
    )

    if args.json:
        payload = [node.model_dump(mode="json") for node in nodes]
        _emit_output(json.dumps(payload, indent=2, ensure_ascii=False), args.output)
        return 0

    lines: list[str] = [
        f"=== Inspeção de Geometria do DOM (Nós encontrados: {len(nodes)}) ==="
    ]
    for i, node in enumerate(nodes, 1):
        status = "VISÍVEL" if node.is_visible else "OCULTO"
        geo = node.geometry
        coords = f"x={geo.x}, y={geo.y}, w={geo.width}, h={geo.height}"
        sel_str = node.selector or node.tag_name
        lines.append(f"[{i}] <{node.tag_name}> {sel_str} | [{status}] | {coords}")
        if node.text_content:
            sample_text = " ".join(node.text_content.split())[:80]
            lines.append(f"    Texto: \"{sample_text}\"")

    _emit_output("\n".join(lines).strip(), args.output)
    return 0


def _handle_visual_diff(args: argparse.Namespace, suite: WebVisualAuditorSuite) -> int:
    """Manipula a execução do subcomando 'visual-diff'."""
    diff_res = suite.run_visual_audit(
        baseline=args.baseline,
        current=args.current,
        diff_out=args.diff_out,
        tolerance=args.tolerance,
    )

    if args.json:
        _emit_output(diff_res.model_dump_json(indent=2), args.output)
        return 1 if diff_res.has_divergence else 0

    lines: list[str] = [
        "=== Auditoria Visual Diferencial Pixel a Pixel ===",
        f"Baseline: {diff_res.baseline_path}",
        f"Current:  {diff_res.current_path}",
        f"Dimensões: {diff_res.baseline_dimensions} (Match: {diff_res.dimensions_match})",
        f"Tolerância por canal: {diff_res.channel_tolerance}",
        f"Pixels avaliados:    {diff_res.total_pixels}",
        f"Pixels divergentes:  {diff_res.diff_pixels}",
        f"Percentual de diff:  {diff_res.diff_percentage:.4f}%",
        f"Status de regressão: {'DIVERGÊNCIA DETECTADA' if diff_res.has_divergence else 'SEM DIVERGÊNCIA'}",
    ]
    if diff_res.diff_output_path:
        lines.append(f"Máscara diferencial: {diff_res.diff_output_path}")

    _emit_output("\n".join(lines), args.output)
    return 1 if diff_res.has_divergence else 0


def _handle_component_diff(args: argparse.Namespace, suite: WebVisualAuditorSuite) -> int:
    """Manipula a execução do subcomando 'component-diff'."""
    selectors = _parse_selectors(args.selectors)
    if not selectors:
        sys.stderr.write("Erro: É obrigatório fornecer ao menos um seletor CSS (--selectors).\n")
        return 1

    reports = suite.run_component_audit(
        baseline=args.baseline,
        current=args.current,
        selectors=selectors,
        diff_dir=args.diff_dir,
    )

    has_divergence = any(
        r.status == "diverged"
        or (r.diff_result is not None and r.diff_result.has_divergence)
        for r in reports
    )

    if args.json:
        payload = [r.model_dump(mode="json") for r in reports]
        _emit_output(json.dumps(payload, indent=2, ensure_ascii=False), args.output)
        return 1 if has_divergence else 0

    lines: list[str] = [
        f"=== Auditoria de Micro-Componentes (Seletores: {len(reports)}) ===",
        f"Baseline: {args.baseline}",
        f"Current:  {args.current}",
        "",
    ]
    for r in reports:
        status_label = r.status.upper()
        diff_info = ""
        if r.diff_result:
            diff_info = f" | Diff: {r.diff_result.diff_percentage:.2f}% ({r.diff_result.diff_pixels} px)"
        lines.append(f"- Seletor: '{r.selector}' -> [{status_label}]{diff_info}")
        if r.geometry_changed:
            lines.append("  Alteração dimensional/posicional detectada.")

    _emit_output("\n".join(lines).strip(), args.output)
    return 1 if has_divergence else 0


def _handle_suite(args: argparse.Namespace, suite: WebVisualAuditorSuite) -> int:
    """Manipula a execução do subcomando 'suite'."""
    selectors = _parse_selectors(args.selectors)
    config = SuiteConfig(
        baseline_url=args.baseline,
        current_url=args.current,
        component_selectors=selectors,
        search_query=args.query,
        tolerance=args.tolerance,
        output_dir=args.output_dir,
        diff_fullpage_name=args.diff_out,
        save_report_json=bool(args.output or args.json),
    )

    report = suite.run_full_suite(config)

    if args.json:
        _emit_output(report.model_dump_json(indent=2), args.output)
        return 1 if report.overall_status == "FAIL" else 0

    lines: list[str] = [
        "==================================================================",
        "              WEB VISUAL AUDITOR — RELATÓRIO DA SUÍTE             ",
        "==================================================================",
        f"Status Global:     [{report.overall_status}]",
        f"Timestamp UTC:     {report.timestamp.isoformat()}",
        f"Baseline:          {report.baseline_url}",
        f"Current:           {report.current_url}",
        "------------------------------------------------------------------",
        "MÉTRICAS CONSOLIDADAS:",
    ]
    for k, v in report.summary_metrics.items():
        lines.append(f"  - {k}: {v}")

    if report.visual_diff:
        lines.append("------------------------------------------------------------------")
        lines.append(
            f"Diff Fullpage:     {report.visual_diff.diff_percentage:.4f}% "
            f"({report.visual_diff.diff_pixels} pixels divergentes)"
        )
        if report.visual_diff.diff_output_path:
            lines.append(f"Máscara Salva:     {report.visual_diff.diff_output_path}")

    if report.component_diffs:
        lines.append("------------------------------------------------------------------")
        lines.append(f"Micro-Componentes Auditados ({len(report.component_diffs)}):")
        for comp in report.component_diffs:
            lines.append(f"  - [{comp.status.upper()}] {comp.selector}")

    lines.append("==================================================================")

    _emit_output("\n".join(lines), args.output)
    return 1 if report.overall_status == "FAIL" else 0


# =============================================================================
# Entrypoint Principal Programático e Executável
# =============================================================================


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada oficial para execução via CLI ou chamada programática.

    Args:
        argv: Lista opcional de argumentos de linha de comando.
              Se None, lê diretamente de sys.argv[1:].

    Returns:
        Código de saída POSIX inteiro:
        - 0: Sucesso e sem divergências visuais.
        - 1: Divergência visual encontrada OU erro de execução.
        - 2: Erro de sintaxe nos argumentos.
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()

    if not argv:
        parser.print_help()
        return 0

    try:
        args = parser.parse_args(argv)
    except SystemExit as sys_exit:
        return int(sys_exit.code) if sys_exit.code is not None else 2

    # Verifica se algum subcomando foi escolhido
    if not args.subcommand:
        parser.print_help()
        return 0

    # Inicializa suíte
    suite = WebVisualAuditorSuite(offline_mode=getattr(args, "offline", False))

    try:
        if args.subcommand == "search":
            return _handle_search(args, suite)
        if args.subcommand == "dom-inspect":
            return _handle_dom_inspect(args, suite)
        if args.subcommand == "visual-diff":
            return _handle_visual_diff(args, suite)
        if args.subcommand == "component-diff":
            return _handle_component_diff(args, suite)
        if args.subcommand == "suite":
            return _handle_suite(args, suite)

        sys.stderr.write(f"Subcomando desconhecido: '{args.subcommand}'\n")
        return 2

    except AuditorError as aud_err:
        sys.stderr.write(f"Erro de auditoria: {aud_err}\n")
        return 1
    except Exception as exc:
        logger.exception("Exceção não tratada durante execução da CLI")
        sys.stderr.write(f"Erro inesperado: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
