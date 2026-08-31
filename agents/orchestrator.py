"""Orquestrador Stateful Principal com Gemini Interactions API e Delegação Especializada."""

import os
from typing import Any

from agents.specialized.security_guard import SecurityGuardAgent
from agents.specialized.sql_specialist import SqlSpecialistAgent
from agents.specialized.workspace_specialist import WorkspaceSpecialistAgent
from shared.context_utils import TokenBudgetManager, extract_skills_summary
from shared.logger import get_logger
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
        api_key: str | None = None
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.skill_parser = SkillParser()
        self.security_guard = SecurityGuardAgent()
        self.sql_specialist = SqlSpecialistAgent(model_name=self.model_name)
        self.workspace_specialist = WorkspaceSpecialistAgent()
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
            ""
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
        user_message: str
    ) -> dict[str, Any]:
        """Processa a mensagem do usuário executando guardrails, roteamento e interação com o modelo."""
        session = self.get_or_create_session(session_id)
        
        # 1. Auditoria de Segurança Zero-Trust (Guardrail)
        audit_result = self.security_guard.audit_input(user_message)
        if not audit_result["is_safe"]:
            return {
                "session_id": session_id,
                "response": audit_result["reason"],
                "status": "blocked_by_guardrails",
                "tokens_estimated": 0
            }

        sanitized_input = audit_result["sanitized_text"]
        session.add_message("user", sanitized_input)

        # 2. Descoberta Dinâmica de Skills Relevantes
        matched_skills = self.skill_parser.match_skills_by_query(sanitized_input)
        system_instruction = self.build_system_prompt(matched_skills)

        # 3. Roteamento Especializado (Se aplicável)
        specialist_results = []
        if any(w in sanitized_input.lower() for w in ["sql", "bigquery", "tabela", "query"]):
            logger.info("Delegando subtarefa para SqlSpecialistAgent...")
            sql_res = self.sql_specialist.execute_task(sanitized_input)
            specialist_results.append(sql_res)

        if any(w in sanitized_input.lower() for w in ["workspace", "pastas", "diretório", "arquivos"]):
            logger.info("Delegando subtarefa para WorkspaceSpecialistAgent...")
            ws_res = self.workspace_specialist.scan_workspace()
            specialist_results.append(ws_res)

        # 4. Geração de Resposta via Gemini Interactions API ou Fallback
        response_text = ""
        interaction_id = None

        if self.client:
            try:
                # Utiliza o Gemini Interactions API (Stateful com previous_interaction_id)
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
                response_text = self._generate_local_fallback(sanitized_input, specialist_results, matched_skills)
        else:
            response_text = self._generate_local_fallback(sanitized_input, specialist_results, matched_skills)

        # 5. Auditoria de Saída
        output_audit = self.security_guard.audit_output(response_text)
        final_output = output_audit["output_text"]
        session.add_message("assistant", final_output)

        tokens_est = self.budget_manager.estimate_tokens(sanitized_input + final_output)

        return {
            "session_id": session_id,
            "interaction_id": interaction_id,
            "response": final_output,
            "matched_skills": matched_skills,
            "delegated_subagents": [r.get("agent") for r in specialist_results],
            "tokens_estimated": tokens_est,
            "status": "success"
        }

    def _generate_local_fallback(
        self,
        user_input: str,
        specialist_results: list[dict[str, Any]],
        matched_skills: list[str]
    ) -> str:
        """Gera resposta estruturada local quando executando offline."""
        output_lines = [
            f"**[MasterOrchestrator - Modelo: {self.model_name}]**",
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

        output_lines.append("\n✅ *Separação estrita de responsabilidades e guardrails Zero-Trust aplicados com sucesso.*")
        return "\n".join(output_lines)
