"""Testes unitários do CodeConsistencySpecialistAgent (Anti-Drift e Sincronização Periódica de Contexto)."""

from agents.orchestrator import MasterOrchestrator
from agents.router import AutoSkillRouter
from agents.specialized.code_consistency_specialist import (
    CodeConsistencySpecialistAgent,
    CodeContract,
)


def test_should_trigger_sync_every_x_steps():
    """Valida o gatilho determinístico a cada X steps."""
    agent = CodeConsistencySpecialistAgent(default_sync_interval=3)

    assert agent.should_trigger_sync(0) is False
    assert agent.should_trigger_sync(1) is False
    assert agent.should_trigger_sync(2) is False
    assert agent.should_trigger_sync(3) is True
    assert agent.should_trigger_sync(4) is False
    assert agent.should_trigger_sync(5) is False
    assert agent.should_trigger_sync(6) is True

    # Intervalo customizado
    assert agent.should_trigger_sync(4, interval=2) is True
    assert agent.should_trigger_sync(5, interval=2) is False


def test_audit_syntax_and_conventions():
    """Valida a detecção de erros de sintaxe e quebra de convenções (ex: BLE001)."""
    agent = CodeConsistencySpecialistAgent()

    # Código limpo
    valid_code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    issues_valid = agent.audit_syntax_and_ast(valid_code)
    assert len(issues_valid) == 0

    # Erro de sintaxe
    invalid_code = "def broken(a, b\n    return a"
    issues_syntax = agent.audit_syntax_and_ast(invalid_code)
    assert len(issues_syntax) == 1
    assert issues_syntax[0].severity == "error"
    assert issues_syntax[0].category == "syntax_error"

    # Violação de convenção: except Exception sem noqa
    bad_except_code = "try:\n    x = 1\nexcept Exception as e:\n    pass\n"
    issues_except = agent.audit_syntax_and_ast(bad_except_code)
    assert any(i.category == "convention_violation" for i in issues_except)


def test_contract_compatibility_and_drift():
    """Valida que quebras de contratos de assinaturas são apontadas como drift."""
    agent = CodeConsistencySpecialistAgent()

    # Registra contrato acordado
    agent.register_contract(
        CodeContract(
            name="fetch_user_profile",
            contract_type="function",
            file_path="services/user.py",
            signature="def fetch_user_profile(user_id: str, timeout: int = 10)",
            description="Busca perfil de usuário",
        )
    )

    # Assinatura incompatível proposta
    proposed = {"fetch_user_profile": "def fetch_user_profile(id_only)"}
    drifts = agent.check_contract_compatibility(proposed, file_path="new_module.py")
    assert len(drifts) == 1
    assert drifts[0].severity == "error"
    assert drifts[0].category == "contract_drift"
    assert "Incompatibilidade de contrato" in drifts[0].description


def test_analyze_step_and_snapshot_generation():
    """Valida a geração do snapshot consolidado e formatação em XML para outros agentes."""
    agent = CodeConsistencySpecialistAgent(default_sync_interval=2)

    sample_code = """
from pydantic import BaseModel

class UserPayload(BaseModel):
    user_id: str
    email: str

def process_user(payload: UserPayload) -> bool:
    return True
"""
    snapshot = agent.analyze_step(
        step_index=2,
        code_snippets=[("models/user.py", sample_code)],
        context_summary="Criando pipeline de usuários",
    )

    assert snapshot.is_sync_turn is True
    assert snapshot.status == "aligned"
    assert "UserPayload" in snapshot.active_contracts
    assert "process_user" in snapshot.active_contracts
    assert len(snapshot.shared_directives_for_agents) > 0

    # Validação do XML gerado para os outros subagentes
    xml_output = agent.format_prompt_injection_for_peers(snapshot)
    assert "<code_context_sync>" in xml_output
    assert "<step_index>2</step_index>" in xml_output
    assert "<contract name=\"UserPayload\"" in xml_output
    assert "</code_context_sync>" in xml_output


def test_router_routes_to_code_consistency_specialist():
    """Garante que o router classifica a intenção de análise de código e anti-drift."""
    router = AutoSkillRouter()
    decision = router.route("por favor faça a analise de codigo e veja se tem desvio de codigo")
    assert decision["target_skill"] == "code_consistency_specialist"
    assert decision["target_type"] == "agent"


def test_orchestrator_delegates_to_code_consistency_specialist():
    """Valida a integração completa com o MasterOrchestrator."""
    orchestrator = MasterOrchestrator()
    user_msg = (
        "Por favor faça a analise de codigo do seguinte trecho:\n"
        "```python\ndef calculate_metric(a: int, b: int) -> int:\n    return a * b\n```"
    )
    result = orchestrator.process_message(session_id="test_consistency_session", user_message=user_msg)

    assert result["status"] == "success"
    assert "CodeConsistencySpecialistAgent" in result["delegated_subagents"]
    assert "Painel de Despacho" in result["response"] or "PAINEL DE DESPACHO" in result["response"]

