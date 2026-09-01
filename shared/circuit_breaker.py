"""Sentinela de Resiliência e Disjuntor de Execução (Circuit Breaker) para Agentes e Grafos."""

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from shared.logger import get_logger

logger = get_logger("CircuitBreaker")


class CircuitState(Enum):
    CLOSED = "CLOSED"  # Fluxo normal autorizado
    HALF_OPEN = "HALF_OPEN"  # Estado de vigilância supervisionada (HITL)
    OPEN = "OPEN"  # Disjuntor desarmado: execução bloqueada


class CircuitTripException(Exception):
    """Exceção levantada quando o disjuntor desarma."""

    def __init__(self, reason: str, payload: dict[str, Any]):
        super().__init__(reason)
        self.reason = reason
        self.payload = payload


@dataclass
class CircuitPolicy:
    """Limiares operacionais para proteção de sessão."""

    max_steps_per_session: int = 25
    max_token_budget: int = 150000
    max_identical_consecutive_states: int = 3
    max_consecutive_errors: int = 3
    timeout_per_step_sec: float = 60.0


@dataclass
class SessionMetrics:
    """Métricas em memória de uma sessão monitorada."""

    session_id: str
    current_step: int = 0
    total_tokens_consumed: int = 0
    consecutive_errors: int = 0
    state: CircuitState = CircuitState.CLOSED
    last_payload_hashes: list[str] = None
    trip_reason: str | None = None

    def __post_init__(self):
        if self.last_payload_hashes is None:
            self.last_payload_hashes = []


class ResilienceCircuitBreaker:
    """Disjuntor determinístico contra loops infinitos, deadlocks e estouro de cota."""

    def __init__(self, policy: CircuitPolicy | None = None):
        self.policy = policy or CircuitPolicy()
        self._sessions: dict[str, SessionMetrics] = {}

    def get_or_create_session(self, session_id: str) -> SessionMetrics:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionMetrics(session_id=session_id)
        return self._sessions[session_id]

    def _hash_payload(self, payload: Any) -> str:
        """Gera hash SHA-256 determinístico de entradas/saídas para detecção de deadlock."""
        try:
            serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        except Exception:  # noqa: BLE001
            serialized = str(payload)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def before_node_execution(
        self,
        session_id: str,
        node_id: str,
        input_payload: Any,
        estimated_tokens: int = 0,
    ) -> None:
        """Valida se o fluxo pode prosseguir antes de executar um agente ou tool."""
        session = self.get_or_create_session(session_id)

        # 1. Se já está desarmado, bloqueia
        if session.state == CircuitState.OPEN:
            raise CircuitTripException(
                f"[CIRCUIT_OPEN] Execução bloqueada na sessão '{session_id}'. Motivo: {session.trip_reason}",
                self.get_status_payload(session_id),
            )

        # 2. Incrementa métricas
        session.current_step += 1
        session.total_tokens_consumed += estimated_tokens

        # 3. Validação de teto de passos
        if session.current_step > self.policy.max_steps_per_session:
            self._trip(
                session,
                f"[MAX_STEPS_EXCEEDED] Sessão excedeu o limite de {self.policy.max_steps_per_session} passos.",
            )

        # 4. Validação de teto de tokens
        if session.total_tokens_consumed > self.policy.max_token_budget:
            self._trip(
                session,
                f"[TOKEN_BUDGET_EXCEEDED] Consumo de {session.total_tokens_consumed} tokens ultrapassou o orçamento de {self.policy.max_token_budget}.",
            )

        # 5. Detecção de loop / deadlock
        payload_hash = self._hash_payload(input_payload)
        session.last_payload_hashes.append(payload_hash)
        if len(session.last_payload_hashes) > self.policy.max_identical_consecutive_states:
            session.last_payload_hashes.pop(0)

        if (
            len(session.last_payload_hashes) >= self.policy.max_identical_consecutive_states
            and len(set(session.last_payload_hashes)) == 1
        ):
            self._trip(
                session,
                f"[DEADLOCK_LOOP_DETECTED] Nó '{node_id}' recebeu payloads idênticos por {self.policy.max_identical_consecutive_states} ciclos seguidos.",
            )

    def after_node_execution(
        self,
        session_id: str,
        node_id: str,
        is_error: bool = False,
        error_msg: str = "",
    ) -> None:
        """Atualiza telemetria após execução do nó."""
        session = self.get_or_create_session(session_id)
        if is_error:
            session.consecutive_errors += 1
            if session.consecutive_errors >= self.policy.max_consecutive_errors:
                self._trip(
                    session,
                    f"[CONSECUTIVE_ERRORS] Nó '{node_id}' falhou {session.consecutive_errors} vezes consecutivas: {error_msg}",
                )
        else:
            session.consecutive_errors = 0

    def _trip(self, session: SessionMetrics, reason: str) -> None:
        """Desarma o circuito."""
        session.state = CircuitState.OPEN
        session.trip_reason = reason
        logger.error(f"🚨 Circuit Breaker DISPARADO na sessão '{session.session_id}': {reason}")
        raise CircuitTripException(reason, self.get_status_payload(session.session_id))

    def reset_circuit(self, session_id: str) -> None:
        """Recuperação manual (HITL) para HALF_OPEN com contadores zerados."""
        session = self.get_or_create_session(session_id)
        session.state = CircuitState.HALF_OPEN
        session.current_step = 0
        session.consecutive_errors = 0
        session.last_payload_hashes.clear()
        session.trip_reason = None
        logger.info(f"Disjuntor da sessão '{session_id}' resetado para HALF_OPEN.")

    def get_status_payload(self, session_id: str) -> dict[str, Any]:
        """Retorna o status estruturado do circuito."""
        session = self.get_or_create_session(session_id)
        can_proceed = session.state != CircuitState.OPEN
        return {
            "session_id": session_id,
            "circuit_status": session.state.value,
            "can_proceed": can_proceed,
            "metrics": {
                "session_steps": session.current_step,
                "accumulated_tokens": session.total_tokens_consumed,
                "consecutive_errors": session.consecutive_errors,
            },
            "trip_reason": session.trip_reason,
            "action_required": "HUMAN_IN_THE_LOOP_APPROVAL" if not can_proceed else None,
        }
