"""Callbacks e ganchos de ciclo de vida para o ADK Lab.

Demonstra:
- before_tool_callback: Interceptação e observabilidade antes da execução de tools.
- after_tool_callback: Registro de telemetria e métricas em state['temp:...'].
- before_model_callback / after_model_callback: Observabilidade de geração de prompts e respostas.
"""

from typing import Any, Optional
from google.adk.agents.context import Context
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from shared.logger import get_logger

logger = get_logger("ADKLabCallbacks")


def lab_before_tool_callback(
    tool: BaseTool, args: dict[str, Any], context: Context
) -> Optional[dict[str, Any]]:
    """Disparado imediatamente antes da invocação de qualquer ferramenta."""
    logger.info(f"[ADK Lab Callback] Invocando tool '{tool.name}' com args: {args}")
    # Registra no state da sessão para auditoria em tempo real
    if hasattr(context, "state") and context.state is not None:
        context.state["temp:active_tool"] = tool.name
    return None


def lab_after_tool_callback(
    tool: BaseTool, args: dict[str, Any], result: dict[str, Any], context: Context
) -> Optional[dict[str, Any]]:
    """Disparado após a execução da ferramenta, permitindo registrar métricas."""
    logger.info(f"[ADK Lab Callback] Tool '{tool.name}' finalizada com status={result.get('status', 'ok')}")
    if hasattr(context, "state") and context.state is not None:
        context.state["temp:last_executed_tool"] = tool.name
    return None


def lab_before_model_callback(
    context: Context, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Observa o envio de requisições ao Gemini."""
    logger.info(f"[ADK Lab Callback] Enviando requisição ao modelo: {llm_request.model}")
    return None


def lab_after_model_callback(
    context: Context, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Observa o retorno do Gemini após a inferência."""
    logger.info("[ADK Lab Callback] Resposta do modelo recebida com sucesso.")
    return None
