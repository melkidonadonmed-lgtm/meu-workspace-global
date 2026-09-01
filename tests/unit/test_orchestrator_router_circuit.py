"""Testes Unitários dos Motores de Orquestração, Router e Circuit Breaker."""

import pytest

from agents.router import AutoSkillRouter
from shared.circuit_breaker import (
    CircuitPolicy,
    CircuitState,
    CircuitTripException,
    ResilienceCircuitBreaker,
)
from skills.skill_factory import SkillFactory
from skills.skill_healthcheck import SkillHealthChecker


def test_router_destructive_gate():
    """Garante que o AutoSkillRouter bloqueia operações destrutivas."""
    router = AutoSkillRouter()
    res = router.route("apagar todas as tabelas do banco de dados")
    assert res["is_destructive"] is True
    assert res["execution_mode"] == "HITL_BLOCK"
    assert res["target_skill"] == "accidental-data-loss-prevention"


def test_router_trivial_bypass():
    """Garante que o AutoSkillRouter responde saudações diretamente."""
    router = AutoSkillRouter()
    res = router.route("Olá, bom dia!")
    assert res["is_destructive"] is False
    assert res["execution_mode"] == "DIRECT_RESPONSE"


def test_router_skill_matching():
    """Garante o roteamento para a skill especialista correta."""
    router = AutoSkillRouter()
    res = router.route("Preciso de uma análise de risco no código linha a linha")
    assert res["target_skill"] == "code-validator"
    assert res["execution_mode"] == "SINGLE_SKILL"


def test_circuit_breaker_normal_and_trip():
    """Garante o funcionamento normal e desarme por deadlock do Circuit Breaker."""
    policy = CircuitPolicy(max_identical_consecutive_states=3)
    cb = ResilienceCircuitBreaker(policy=policy)
    session_id = "test_cb_session"

    # Passos normais com payloads diferentes
    cb.before_node_execution(session_id, "node1", "payload 1")
    cb.after_node_execution(session_id, "node1", is_error=False)

    cb.before_node_execution(session_id, "node1", "payload 2")
    cb.after_node_execution(session_id, "node1", is_error=False)

    # 3 payloads idênticos consecutivos disparam deadlock
    cb.before_node_execution(session_id, "node1", "payload repetido")
    cb.before_node_execution(session_id, "node1", "payload repetido")

    with pytest.raises(CircuitTripException) as exc_info:
        cb.before_node_execution(session_id, "node1", "payload repetido")

    assert "DEADLOCK_LOOP_DETECTED" in exc_info.value.reason
    status = cb.get_status_payload(session_id)
    assert status["circuit_status"] == CircuitState.OPEN.value
    assert status["can_proceed"] is False

    # Reset HITL
    cb.reset_circuit(session_id)
    assert cb.get_status_payload(session_id)["circuit_status"] == CircuitState.HALF_OPEN.value


def test_skill_healthchecker_audit():
    """Garante que a auditoria de healthcheck do catálogo esteja 100% íntegra."""
    checker = SkillHealthChecker()
    report = checker.audit_catalog()
    assert report["status"] == "healthy"
    assert report["is_healthy"] is True
    assert report["total_issues"] == 0
    assert report["total_skills"] >= 10


def test_skill_factory_validation(tmp_path):
    """Garante que a SkillFactory valida kebab-case e descrições mínimas."""
    factory = SkillFactory(skills_dir=tmp_path)

    # Erro de kebab-case
    with pytest.raises(ValueError) as exc:
        factory.create_skill(name="Invalid_Name", description="Descricao longa o suficiente para passar no teste")
    assert "kebab-case" in str(exc.value)

    # Erro de descrição curta
    with pytest.raises(ValueError) as exc_desc:
        factory.create_skill(name="valid-name", description="curta")
    assert "no mínimo 20 caracteres" in str(exc_desc.value)

    # Criação válida
    res = factory.create_skill(
        name="minha-nova-skill",
        description="Esta é uma descrição técnica válida para a nova habilidade modular.",
        category="custom",
    )
    assert res["status"] == "success"
    assert (tmp_path / "custom" / "minha-nova-skill" / "SKILL.md").exists()
