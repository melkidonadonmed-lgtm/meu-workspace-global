"""Orquestrador Stateful Principal com Gemini Interactions API, Router e Circuit Breaker."""

import os
from typing import Any

from agents.router import AutoSkillRouter
from agents.specialized.html_modular_specialist import HTMLModularSpecialistAgent
from agents.specialized.research_evolution_specialist import (
    ResearchEvolutionSpecialistAgent,
    ResearchTaskRequest,
)
from agents.specialized.security_guard import SecurityGuardAgent
from agents.specialized.sql_specialist import SqlSpecialistAgent
from agents.specialized.workspace_specialist import WorkspaceSpecialistAgent
from shared.circuit_breaker import CircuitTripException, ResilienceCircuitBreaker
from shared.context_utils import TokenBudgetManager, extract_skills_summary
from shared.logger import get_logger
from shared.state_orchestrator import StateOrchestrator
from skills.skill_factory import SkillFactory
from skills.skill_parser import SkillParser

logger = get_logger("MasterOrchestrator")


class SessionState:
    """Representação de estado da sessão do usuário com histórico encadeado."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: list[dict[str, str]] = []
        self.last_interaction_id: str | None = None
        self.context_memory: dict[str, Any] = {}

    def add_message(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})


class MasterOrchestrator:
    """Orquestrador Central Stateful do Ecossistema Global."""

    def __init__(
        self,
        model_name: str = "gemini-3.7-flash",
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.skill_parser = SkillParser()
        self.skill_factory = SkillFactory()
        self.router = AutoSkillRouter()
        self.circuit_breaker = ResilienceCircuitBreaker()
        self.state_orchestrator = StateOrchestrator()
        self.security_guard = SecurityGuardAgent()
        self.sql_specialist = SqlSpecialistAgent(model_name=self.model_name)
        self.workspace_specialist = WorkspaceSpecialistAgent()
        self.html_modular_specialist = HTMLModularSpecialistAgent(model_name=self.model_name)
        self.research_evolution_specialist = ResearchEvolutionSpecialistAgent(model_name=self.model_name)
        self.budget_manager = TokenBudgetManager()
        self.sessions: dict[str, SessionState] = {}
        self._init_gemini_client()

    def _init_gemini_client(self) -> None:
        """Inicializa o cliente do Google GenAI Interactions API se a chave estiver presente."""
        self.client = None
        if self.api_key:
            try:
                from google import genai

                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Cliente Google GenAI inicializado com sucesso (Modelo: {self.model_name}).")
            except Exception as e:  # noqa: BLE001 - fallback proposital para modo local
                logger.warning(f"Não foi possível inicializar google-genai client: {e}. Executando em modo local.")
        else:
            logger.info("Nenhuma GEMINI_API_KEY encontrada. Executando em modo simulado/local.")

    def get_or_create_session(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)
        return self.sessions[session_id]

    def build_system_prompt(self, matched_skills: list[str]) -> str:
        """Constrói dinamicamente o System Prompt com injeção sob demanda de skills relevantes."""
        available_skills = self.skill_parser.list_available_skills()
        skills_summary = extract_skills_summary(available_skills)

        prompt_parts = [
            "Você é o Orquestrador Central de um Ecossistema de Agentes Autônomos de Alta Performance.",
            "Você opera sob o princípio da separação estrita de responsabilidades.",
            "",
            skills_summary,
            "",
        ]

        if matched_skills:
            prompt_parts.append("## Habilidades Específicas Carregadas para Esta Requisição:")
            for s_id in matched_skills:
                content = self.skill_parser.get_skill_full_content(s_id)
                if content:
                    prompt_parts.append(f"\n### [SKILL: {s_id}]\n{content}\n")

        prompt_parts.append("Responda sempre com precisão técnica máxima, clareza e em Português BR.")
        return "\n".join(prompt_parts)

    def process_message(
        self,
        session_id: str,
        user_message: str,
    ) -> dict[str, Any]:
        """Processa a mensagem do usuário executando guardrails, roteamento e interação com o modelo."""
        session = self.get_or_create_session(session_id)

        # 1. Sentinela de Resiliência: Interceptor pré-execução
        estimated_input_tokens = self.budget_manager.estimate_tokens(user_message)
        try:
            self.circuit_breaker.before_node_execution(
                session_id=session_id,
                node_id="MasterOrchestrator",
                input_payload=user_message,
                estimated_tokens=estimated_input_tokens,
            )
        except CircuitTripException as trip_err:
            return {
                "session_id": session_id,
                "response": f"🚨 Execução interrompida pelo Circuit Breaker: {trip_err.reason}",
                "status": "circuit_breaker_tripped",
                "circuit_payload": trip_err.payload,
                "matched_skills": [],
                "routing_decision": None,
                "delegated_subagents": [],
                "checkpoint_persisted": False,
                "tokens_estimated": 0,
            }

        # 2. Auditoria de Segurança Zero-Trust (Guardrail)
        audit_result = self.security_guard.audit_input(user_message)
        if not audit_result["is_safe"]:
            self.circuit_breaker.after_node_execution(
                session_id, "MasterOrchestrator", is_error=True, error_msg="Blocked by guardrail"
            )
            return {
                "session_id": session_id,
                "response": audit_result["reason"],
                "status": "blocked_by_guardrails",
                "matched_skills": [],
                "routing_decision": None,
                "delegated_subagents": [],
                "checkpoint_persisted": False,
                "tokens_estimated": 0,
            }

        sanitized_input = audit_result["sanitized_text"]
        session.add_message("user", sanitized_input)
        input_persisted = self.state_orchestrator.save_checkpoint(
            session_id=session_id,
            step_index=len(session.history),
            agent_name="MasterOrchestrator",
            role="user",
            content=sanitized_input,
        )

        # 3. Roteamento Inteligente de Intenções (AutoSkillRouter)
        routing_decision = self.router.route(sanitized_input)
        if routing_decision.get("is_destructive"):
            return {
                "session_id": session_id,
                "response": (
                    "⚠️ **Operação Destrutiva Bloqueada pelos Guardrails Zero-Trust**\n\n"
                    "A ação solicitada envolve exclusão ou mutação potencialmente irreversível. "
                    "Por favor, confirme explicitamente se deseja prosseguir com a execução."
                ),
                "status": "blocked_by_guardrails",
                "routing_decision": routing_decision,
                "matched_skills": [],
                "delegated_subagents": [],
                "checkpoint_persisted": input_persisted,
                "tokens_estimated": 0,
            }

        # 4. Descoberta e injeção de skills relevantes
        matched_skills = self.skill_parser.match_skills_by_query(sanitized_input)
        target_skill = routing_decision.get("target_skill")
        target_type = routing_decision.get("target_type")
        if target_skill and target_type == "skill" and target_skill not in matched_skills:
            matched_skills.append(target_skill)

        system_instruction = self.build_system_prompt(matched_skills)

        # 5. Roteamento Especializado de Subagentes
        specialist_results = []
        if any(w in sanitized_input.lower() for w in ["sql", "bigquery", "tabela", "query"]):
            logger.info("Delegando subtarefa para SqlSpecialistAgent...")
            sql_res = self.sql_specialist.execute_task(sanitized_input)
            specialist_results.append(sql_res)

        if any(w in sanitized_input.lower() for w in ["workspace", "pastas", "diretório", "arquivos"]):
            logger.info("Delegando subtarefa para WorkspaceSpecialistAgent...")
            ws_res = self.workspace_specialist.scan_workspace()
            specialist_results.append(ws_res)

        if any(w in sanitized_input.lower() for w in ["pesquisar", "pesquisa profunda", "investigar", "pesquisa tecnica", "pesquisa técnica"]):
            logger.info("Delegando subtarefa para ResearchEvolutionSpecialistAgent...")
            research_res = self.research_evolution_specialist.execute_research(
                ResearchTaskRequest(query=sanitized_input)
            )
            specialist_results.append({"agent": "ResearchEvolutionSpecialistAgent", **research_res.model_dump()})
        elif not matched_skills and target_type == "none" and routing_decision.get("complexity") == "COMPLEXO":
            # Gap operacional: nenhuma skill/agente cobre uma demanda complexa. Aciona a SkillFactory
            # (via ResearchEvolutionSpecialistAgent) para desenhar um rascunho de SKILL.md antes de prosseguir.
            logger.info("Gap operacional detectado. Acionando geração autônoma de skill (SkillFactory)...")
            gap_res = self.research_evolution_specialist.execute_research(
                ResearchTaskRequest(query=sanitized_input, auto_generate_skill=True)
            )
            specialist_results.append({"agent": "ResearchEvolutionSpecialistAgent", **gap_res.model_dump()})
            if gap_res.generated_skill and gap_res.generated_skill.get("status") == "created_and_validated":
                self.skill_parser.reload_skills()

        # 6. Geração de Resposta via Gemini Interactions API ou Fallback
        response_text = ""
        interaction_id = None

        if self.client:
            try:
                kwargs: dict[str, Any] = {
                    "model": self.model_name,
                    "input": sanitized_input,
                    "system_instruction": system_instruction,
                }
                if session.last_interaction_id:
                    kwargs["previous_interaction_id"] = session.last_interaction_id

                interaction = self.client.interactions.create(**kwargs)
                response_text = interaction.output_text or "Processado sem saída de texto."
                session.last_interaction_id = interaction.id
                interaction_id = interaction.id
            except Exception as e:  # noqa: BLE001 - fallback proposital para modo local
                logger.error(f"Falha na chamada ao Gemini Interactions API: {e}")
                response_text = self._generate_local_fallback(
                    sanitized_input, specialist_results, matched_skills, routing_decision
                )
        else:
            response_text = self._generate_local_fallback(
                sanitized_input, specialist_results, matched_skills, routing_decision
            )

        # 7. Auditoria de Saída
        output_audit = self.security_guard.audit_output(response_text)
        dispatch_panel = self._build_dispatch_panel(sanitized_input, matched_skills, routing_decision)
        final_output = f"{dispatch_panel}\n{output_audit['output_text']}"
        session.add_message("assistant", final_output)

        # 8. Checkpointing Transacional e Conclusão no Circuit Breaker
        output_persisted = self.state_orchestrator.save_checkpoint(
            session_id=session_id,
            step_index=len(session.history),
            agent_name="MasterOrchestrator",
            role="assistant",
            content=final_output,
            metadata={"matched_skills": matched_skills, "routing_mode": routing_decision.get("execution_mode")},
        )
        self.circuit_breaker.after_node_execution(session_id, "MasterOrchestrator", is_error=False)

        tokens_est = self.budget_manager.estimate_tokens(sanitized_input + final_output)

        return {
            "session_id": session_id,
            "interaction_id": interaction_id,
            "response": final_output,
            "matched_skills": matched_skills,
            "routing_decision": routing_decision,
            "delegated_subagents": [r.get("agent") for r in specialist_results],
            "tokens_estimated": tokens_est,
            "checkpoint_persisted": input_persisted and output_persisted,
            "status": "success",
        }

    def _build_dispatch_panel(self, user_input: str, matched_skills: list[str], routing_decision: dict[str, Any]) -> str:
        """Monta o Painel de Despacho Executivo com o mapa real de roteamento desta requisição."""
        target = routing_decision.get("target_skill") or "Resposta Direta (sem delegação)"
        target_type = routing_decision.get("target_type", "none")
        type_label = {"skill": "Skill do Catálogo", "agent": "Subagente Especialista", "meta": "Orquestrador (Cascata Multi-Agente)", "none": "N/A"}.get(target_type, target_type)
        capacidade = "Existente no Catálogo" if (target_type == "skill" and target in matched_skills) or target_type in ("agent", "meta") else "Sem correspondência direta"

        return "\n".join(
            [
                "[PAINEL DE DESPACHO EXECUTIVO]",
                f"- Intenção Identificada: {user_input[:100]}",
                f"- Módulo Acionado: {target} ({type_label})",
                f"- Matriz de Skill Carregada: {', '.join(matched_skills) if matched_skills else 'Nenhuma skill específica injetada'}",
                f"- Status de Capacidade: {capacidade}",
                "-" * 70,
            ]
        )

    def _generate_local_fallback(
        self,
        user_input: str,
        specialist_results: list[dict[str, Any]],
        matched_skills: list[str],
        routing_decision: dict[str, Any],
    ) -> str:
        """Gera resposta estruturada local quando executando offline."""
        complexity = routing_decision.get("complexity", "INTERMEDIARIO")
        mode = routing_decision.get("execution_mode", "SINGLE_SKILL")

        output_lines = [
            f"**[MasterOrchestrator - Modelo: {self.model_name}]**",
            f"📊 *Modo de Roteamento:* `{mode}` | *Complexidade:* `{complexity}`",
            "",
            "Sua requisição foi processada com sucesso no ecossistema global unificado.",
        ]

        if matched_skills:
            output_lines.append(f"\n🧩 **Habilidades Injetadas:** `{', '.join(matched_skills)}`")

        if specialist_results:
            output_lines.append("\n🤖 **Resultados de Subagentes Especialistas:**")
            for res in specialist_results:
                agent_name = res.get("agent", "Agente")
                output_lines.append(f"\n- **{agent_name}**:")
                if "suggested_sql" in res:
                    output_lines.append(f"```sql\n{res['suggested_sql']}\n```")
                if "total_items_scanned" in res:
                    output_lines.append(f"Varredura concluída: {res['total_items_scanned']} itens inspecionados.")

        output_lines.append("\n✅ *Separação estrita de responsabilidades, Circuit Breaker e guardrails Zero-Trust aplicados.*")
        return "\n".join(output_lines)
