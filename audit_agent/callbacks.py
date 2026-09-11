"""Callbacks nativos de segurança Zero-Trust para o Google ADK.

Implementa guardrails em tempo de execução para:
1. before_model_guard: Detecção e bloqueio de prompt injection e mascaramento de PII.
2. before_tool_guard: Validação estrita de fronteiras de diretórios (impedindo auto-auditoria fora de projects/*).
3. after_model_guard: Redação de credenciais e tokens vazados nas respostas.
"""

from typing import Any, Optional
from google.adk.agents.context import Context
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.genai import types

from agents.specialized.security_guard import SecurityGuardAgent
from shared.logger import get_logger

logger = get_logger("AuditAgentCallbacks")
security_guard = SecurityGuardAgent()


def before_model_guard(
    context: Context, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Intercepta o prompt do usuário antes do envio ao Gemini (Zero-Trust)."""
    user_text = ""
    if llm_request.contents:
        last_content = llm_request.contents[-1]
        if hasattr(last_content, "parts") and last_content.parts:
            text_parts = [
                p.text for p in last_content.parts if hasattr(p, "text") and p.text
            ]
            user_text = " ".join(text_parts)

    if user_text:
        audit_res = security_guard.audit_input(user_text)
        if not audit_res.get("is_safe", True):
            logger.warning(f"Injeção de prompt interceptada no ADK: {audit_res.get('reason')}")
            # Retorna resposta imediata sem consumir tokens ou invocar o modelo
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part.from_text(
                            text=f"[BLOQUEIO DE SEGURANCA ZERO-TRUST] {audit_res.get('reason')}"
                        )
                    ],
                )
            )

    return None


def before_tool_guard(
    tool: BaseTool, args: dict[str, Any], context: Context
) -> Optional[dict[str, Any]]:
    """Garante que ferramentas de varredura não acessem pastas proibidas (Anti-Loop)."""
    target = (
        args.get("project_name_or_path")
        or args.get("target_path")
        or args.get("file_path")
    )
    if target:
        is_allowed, msg = security_guard.validate_audit_target(str(target))
        if not is_allowed:
            logger.warning(f"Chamada de ferramenta bloqueada pelo Guardrail de Fronteira: {msg}")
            return {
                "status": "error",
                "code": "TARGET_PROHIBITED",
                "message": msg,
            }

    return None


def after_model_guard(
    context: Context, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Sanitiza o conteúdo gerado pelo Gemini antes da entrega ao usuário."""
    if not llm_response.content or not hasattr(llm_response.content, "parts"):
        return None

    sanitized_parts = []
    has_mutation = False

    for part in llm_response.content.parts:
        if hasattr(part, "text") and part.text:
            audit_out = security_guard.audit_output(part.text)
            new_text = audit_out.get("output_text", part.text)
            if new_text != part.text:
                has_mutation = True
            sanitized_parts.append(types.Part.from_text(text=new_text))
        else:
            sanitized_parts.append(part)

    if has_mutation:
        llm_response.content.parts = sanitized_parts

    return llm_response
