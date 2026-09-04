from agents.orchestrator import MasterOrchestrator
from agents.router import AutoSkillRouter
from agents.specialized.customer_issue_reviewer import CustomerIssueReviewerAgent


def test_customer_issue_reviewer_direct():
    """Garante que o CustomerIssueReviewerAgent executa e retorna relatório formatado."""
    agent = CustomerIssueReviewerAgent()
    result = agent.review_issues("Revisar chamados de clientes")

    assert result["status"] == "completed"
    assert result["agent"] == "CustomerIssueReviewerAgent"
    assert "Chamados" in result["report"]


def test_router_routes_to_customer_issue_reviewer():
    """Garante que o AutoSkillRouter detecta menção a chamados/issues e roteia para o agente."""
    router = AutoSkillRouter()
    decision = router.route("O cliente abriu um chamado urgente relatando problema")

    assert decision["target_skill"] == "customer_issue_reviewer"
    assert decision["target_type"] == "agent"
    assert any(c.get("domain") == "suporte" for c in decision["candidates"])


def test_orchestrator_auto_invokes_customer_issue_reviewer():
    """Garante que o MasterOrchestrator aciona automaticamente o agente ao receber mensagem de chamado."""
    orchestrator = MasterOrchestrator()
    response = orchestrator.process_message(
        session_id="test-issue-session",
        user_message="Por favor, preciso revisar chamado crítico de cliente",
    )

    assert response["status"] in ("success", "completed", "direct_fallback")
    assert "CustomerIssueReviewerAgent" in response.get("delegated_subagents", [])

