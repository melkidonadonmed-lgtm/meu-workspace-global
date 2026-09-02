"""Servidor API Gateway FastAPI com suporte a endpoints REST e SSE Streaming."""

import asyncio
import json
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agents.antigravity_bridge import AntigravityAgentBridge
from agents.orchestrator import MasterOrchestrator
from agents.specialized.html_modular_specialist import HTMLBuildRequest, HTMLBuildResponse
from shared.circuit_breaker import CircuitTripException
from shared.logger import get_logger, setup_logging

setup_logging()
logger = get_logger("APIGateway")

app = FastAPI(
    title="Global Agent Ecosystem API Gateway",
    version="1.1.0",
    description="Gateway de API para orquestração de agentes autônomos, skills e MCP.",
)

# Habilitar CORS para projetos locais e clientes web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instâncias globais
orchestrator = MasterOrchestrator()
antigravity_bridge = AntigravityAgentBridge()


class ChatRequest(BaseModel):
    session_id: str = Field(default="default_session", description="Identificador único da sessão do usuário")
    message: str = Field(..., min_length=1, description="Texto da mensagem enviada pelo usuário")


class ChatResponse(BaseModel):
    session_id: str
    interaction_id: str | None = None
    response: str
    matched_skills: list[str] = Field(default_factory=list)
    routing_decision: dict[str, Any] | None = None
    delegated_subagents: list[str] = Field(default_factory=list)
    tokens_estimated: int
    checkpoint_persisted: bool = True
    status: str


class AntigravityResponse(BaseModel):
    response: str
    status: str
    model: str
    matched_skills: list[str]
    tools_used: list[str]
    workspace_root: str


class CreateSkillRequest(BaseModel):
    name: str = Field(..., min_length=2, description="Nome da skill em kebab-case")
    description: str = Field(..., min_length=20, description="Descrição detalhada e gatilhos da skill")
    category: str = Field(default="custom", description="Categoria/bundle da skill")
    triggers: list[str] | None = Field(default=None, description="Gatilhos de ativação")


@app.get("/health")
def health_check() -> dict[str, Any]:
    """Endpoint de verificação de integridade operacional."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "model": orchestrator.model_name,
        "active_sessions": len(orchestrator.sessions),
        "available_skills": len(orchestrator.skill_parser.list_available_skills()),
        "antigravity_agent_ready": True,
    }


@app.get("/skills")
def list_skills() -> dict[str, Any]:
    """Retorna o inventário de habilidades disponíveis no catálogo."""
    return {"skills": orchestrator.skill_parser.list_available_skills()}


@app.get("/skills/health")
def skills_health() -> dict[str, Any]:
    """Retorna o relatório completo de auditoria do catálogo de skills."""
    return orchestrator.skill_parser.audit_catalog()


@app.post("/skills/create")
def create_skill(request: CreateSkillRequest) -> dict[str, Any]:
    """Cria e registra uma nova skill no catálogo governado."""
    try:
        res = orchestrator.skill_factory.create_skill(
            name=request.name,
            description=request.description,
            category=request.category,
            triggers=request.triggers,
        )
        orchestrator.skill_parser.reload_skills()
        return res
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err)) from val_err
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@app.post("/agents/html/build", response_model=HTMLBuildResponse)
def build_html_page(request: HTMLBuildRequest) -> HTMLBuildResponse:
    """Delega a montagem de página/componentes HTML5 modular ao HTMLModularSpecialistAgent.

    Requer entrada estruturada (componentes tipados) em vez de texto livre, pois o agente
    não deve inferir/inventar parâmetros de construção ausentes (Negative Bounds).
    """
    try:
        return orchestrator.html_modular_specialist.assemble_page(request)
    except Exception as e:
        logger.error(f"Erro ao montar página HTML via HTMLModularSpecialistAgent: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest) -> ChatResponse:
    """Processa uma mensagem do usuário de ponta a ponta."""
    try:
        result = orchestrator.process_message(
            session_id=request.session_id, user_message=request.message
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Erro ao processar mensagem no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/antigravity/chat", response_model=AntigravityResponse)
async def handle_antigravity_chat(request: ChatRequest) -> AntigravityResponse:
    """Processa mensagem utilizando o Google Antigravity Agent Bridge.

    Reutiliza o Circuit Breaker e o StateOrchestrator do MasterOrchestrator para que este
    caminho paralelo também fique protegido contra loops/deadlocks e mantenha trilha de auditoria.
    """
    estimated_tokens = orchestrator.budget_manager.estimate_tokens(request.message)
    try:
        orchestrator.circuit_breaker.before_node_execution(
            session_id=request.session_id,
            node_id="AntigravityAgentBridge",
            input_payload=request.message,
            estimated_tokens=estimated_tokens,
        )
    except CircuitTripException as trip_err:
        raise HTTPException(status_code=429, detail=trip_err.reason) from trip_err

    try:
        result = await antigravity_bridge.chat(request.message)
        orchestrator.state_orchestrator.save_checkpoint(
            session_id=request.session_id,
            step_index=0,
            agent_name="AntigravityAgentBridge",
            role="assistant",
            content=result.get("response", ""),
            metadata={"matched_skills": result.get("matched_skills", [])},
        )
        orchestrator.circuit_breaker.after_node_execution(
            request.session_id, "AntigravityAgentBridge", is_error=False
        )
        return AntigravityResponse(**result)
    except Exception as e:
        orchestrator.circuit_breaker.after_node_execution(
            request.session_id, "AntigravityAgentBridge", is_error=True, error_msg=str(e)
        )
        logger.error(f"Erro ao processar mensagem via Antigravity Agent: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/chat/stream")
async def handle_chat_stream(request: ChatRequest):
    """Endpoint com Server-Sent Events (SSE) para streaming em tempo real."""

    async def event_generator():
        yield f"data: {json.dumps({'event': 'step.start', 'message': 'Iniciando processamento e auditoria Zero-Trust...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)

        result = orchestrator.process_message(
            session_id=request.session_id, user_message=request.message
        )

        full_text = result["response"]
        chunk_size = 50
        for i in range(0, len(full_text), chunk_size):
            chunk = full_text[i : i + chunk_size]
            yield f"data: {json.dumps({'event': 'step.delta', 'delta': chunk}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.05)

        yield f"data: {json.dumps({'event': 'interaction.completed', 'metadata': result}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agents.api_gateway:app", host="0.0.0.0", port=8000, reload=True)
