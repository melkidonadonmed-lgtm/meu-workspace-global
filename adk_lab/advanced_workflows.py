"""Implementação de padrões avançados da ADK 2.0 Dynamic Workflows API.

Demonstra:
1. Data Handling tipado com Pydantic (eliminando estado manual).
2. Sequência de nós (Sequence Route).
3. Execução paralela (Parallel Fan-out / Fan-in com asyncio.gather).
4. Human-in-the-loop com RequestInput.
5. Custom run_id para checkpointing resiliente.
"""

import asyncio
from typing import Any, List
from pydantic import BaseModel
from google.adk import Context, Workflow
from google.adk.events import RequestInput
from google.adk.workflow import node


# ---------------------------------------------------------------------
# 1. Schemas de Dados Tipados (Data Handling)
# ---------------------------------------------------------------------
class ProjectAnalysisReport(BaseModel):
    project_name: str
    status: str
    score: int


# ---------------------------------------------------------------------
# 2. Nós Básicos e Paralelos (@node)
# ---------------------------------------------------------------------
@node(name="worker_analyzer")
def worker_analyzer(node_input: str) -> ProjectAnalysisReport:
    """Nó worker que simula análise estática de um projeto."""
    return ProjectAnalysisReport(
        project_name=node_input,
        status="approved",
        score=95,
    )


# ---------------------------------------------------------------------
# 3. Orquestrador Paralelo (Fan-out / Fan-in com Custom run_id)
# ---------------------------------------------------------------------
@node(name="parallel_auditor", rerun_on_resume=True)
async def parallel_auditor(
    ctx: Context, node_input: str = ""
) -> List[ProjectAnalysisReport]:
    """Dispara a execução de múltiplos workers em paralelo com IDs customizados determinísticos."""
    projects = ["pcm", "canvas_ide", "keepdocs-workspace", "WAOE"]

    # Inicia tarefas assíncronas em paralelo
    tasks = [
        ctx.run_node(
            worker_analyzer,
            node_input=proj,
            run_id=f"audit-{proj}",  # Caractere não-numérico obrigatório para evitar colisão
        )
        for proj in projects
    ]

    # Coleta todas as respostas em paralelo (Fan-in)
    results = await asyncio.gather(*tasks)
    return results


# ---------------------------------------------------------------------
# 4. Nó Human-in-the-Loop (HITL com RequestInput)
# ---------------------------------------------------------------------
@node(rerun_on_resume=False)
async def request_approval_node(ctx: Context, node_input: Any):
    """Pausa o workflow e aguarda decisão humana explícita."""
    yield RequestInput(message="Deseja aprovar o deploy em produção? (Sim/Nao)")


@node(rerun_on_resume=True)
async def approval_workflow(ctx: Context, node_input: str = "") -> str:
    """Orquestrador do processo com passo interativo humano."""
    user_decision = await ctx.run_node(request_approval_node)
    if str(user_decision).strip().lower() in ("sim", "yes", "s"):
        return "DEPLOY_APROVADO"
    return "DEPLOY_REJEITADO"


# ---------------------------------------------------------------------
# 5. Grafos de Workflow Exportáveis
# ---------------------------------------------------------------------
parallel_workflow_agent = Workflow(
    name="parallel_workflow_agent",
    edges=[("START", parallel_auditor)],
)
