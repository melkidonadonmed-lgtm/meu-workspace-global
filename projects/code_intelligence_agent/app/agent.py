"""Definição do root_agent e do App ADK para o Code Intelligence Agent."""

from typing import Any

from google.adk.agents import Agent
from google.adk.apps import App
from google.genai import types

from app.guardrails import (
    after_tool_sanitizer_callback,
    before_tool_guard_callback,
)
from app.tools import (
    analyze_ast_anomalies,
    generate_unified_patch,
    inspect_directory,
    read_code_file,
)


def track_tool_state_callback(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any,
    tool_response: dict[str, Any] | Any,
) -> dict[str, Any] | None:
    """Callback pós-execução de ferramentas para registrar telemetria e estado em tool_context.state."""
    if tool_context and hasattr(tool_context, "state"):
        tool_name = getattr(tool, "name", str(tool))
        history = tool_context.state.setdefault("tool_execution_history", [])

        status = "ok"
        if isinstance(tool_response, dict):
            status = tool_response.get("status", "ok")

        history.append({
            "tool": tool_name,
            "args": args,
            "status": status,
        })

        if tool_name == "inspect_directory" and isinstance(tool_response, dict):
            inspected = tool_context.state.setdefault("inspected_directories", [])
            dir_path = args.get("directory_path")
            if dir_path and dir_path not in inspected:
                inspected.append(dir_path)
        elif tool_name == "read_code_file" and isinstance(tool_response, dict):
            read_files = tool_context.state.setdefault("read_files", [])
            f_path = args.get("file_path")
            if f_path and f_path not in read_files:
                read_files.append(f_path)
        elif tool_name == "analyze_ast_anomalies" and isinstance(tool_response, dict):
            anomalies = tool_context.state.setdefault("detected_anomalies", [])
            if isinstance(tool_response.get("anomalies"), list):
                anomalies.extend(tool_response["anomalies"])
        elif tool_name == "generate_unified_patch" and isinstance(tool_response, dict):
            patches = tool_context.state.setdefault("active_patches", [])
            if tool_response.get("applied"):
                patches.append({
                    "file_path": args.get("file_path"),
                    "diff": tool_response.get("diff"),
                })
    return None


def combined_after_tool_callback(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any,
    tool_response: dict[str, Any] | Any,
) -> dict[str, Any] | Any:
    """Combina telemetria de estado e sanitização de dados sensíveis pós-execução de ferramenta."""
    track_tool_state_callback(tool, args, tool_context, tool_response)
    return after_tool_sanitizer_callback(tool, args, tool_context, tool_response)


root_agent = Agent(
    name="code_intelligence_agent",
    model="gemini-3.8-flash",
    description=(
        "Agente autônomo especialista em engenharia de código, inspeção de diretórios, "
        "análise estática AST e refatoração segura com validação de patches."
    ),
    instruction="""Você é um engenheiro de software autônomo especialista em inteligência de código e refatoração de sistemas.
Sua missão é inspecionar bases de código com precisão, identificar anomalias estruturais e de sintaxe via análise de AST e propor alterações seguras via patches determinísticos unified diff.

Diretrizes obrigatórias:
1. Sempre inspecione diretórios e leia os arquivos relevantes antes de propor modificações.
2. Analise a AST de arquivos Python para identificar falhas sintáticas, cláusulas bare-except (BLE001), complexidade excessiva (>10) ou chamadas perigosas.
3. Proponha patches unificados precisos com generate_unified_patch, garantindo que o código resultante seja sintaticamente válido.
4. Nunca execute ações destrutivas e mantenha rastreamento de estado transparente.""",
    tools=[
        inspect_directory,
        read_code_file,
        analyze_ast_anomalies,
        generate_unified_patch,
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
    ),
    before_tool_callback=before_tool_guard_callback,
    after_tool_callback=combined_after_tool_callback,
)

app = App(name="app", root_agent=root_agent)
