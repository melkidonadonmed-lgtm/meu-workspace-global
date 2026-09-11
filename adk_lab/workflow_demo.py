"""Demonstração da Google ADK 2.0 Graph Workflow API (adk_lab).

Demonstra:
1. Nós declarativos e tipados com o decorador @node.
2. Execução dinâmica de sub-nós em tempo de execução via ctx.run_node().
3. Configuração topológica de grafo com Workflow(edges=[("START", ...)]).
4. Suporte a retomada resiliente de sessões com rerun_on_resume=True.
"""

from typing import Any
from google.adk import Context, Workflow
from google.adk.workflow import node


@node(name="hello_node")
def my_node(node_input: Any) -> str:
    """Nó síncrono que processa a entrada e retorna uma saudação."""
    return f"Hello World (recebido: {node_input})"


@node(name="dynamic_workflow_node", rerun_on_resume=True)
async def my_workflow(ctx: Context, node_input: str = "inicio") -> str:
    """Nó assíncrono dinâmico que orquestra a execução de outros nós via Context."""
    # ctx.run_node executa um nó filho e retorna seu resultado
    result = await ctx.run_node(my_node, node_input="hello_from_workflow")
    return result


# Definição do grafo executável do Workflow
root_agent = Workflow(
    name="workflow_demo_agent",
    edges=[("START", my_workflow)],
)
