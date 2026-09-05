# 🌐 GEMINI.md — Instruções do Workspace Global de Agentes

> Este arquivo fornece as instruções operacionais e contexto para o **Gemini CLI** e o **Google Antigravity (AGY)** ao trabalhar dentro do repositório `meu-workspace-global`. Para a especificação detalhada de arquitetura e catálogo de subagentes, consulte também [AGENTS.md](file:///C:/Users/melki/meu-workspace-global/AGENTS.md).

---

## 🏛️ Visão Geral do Projeto

Repositório global de agentes autônomos, catálogo hierárquico de skills (`SKILL.md`) e motores de orquestração cognitiva (`AutoSkillRouter`, `ResilienceCircuitBreaker`, `SkillHealthChecker`, `SkillFactory`, `StateOrchestrator`).

*   **Idioma Oficial**: Português (BR) para código, documentação, commits e respostas.
*   **Gerenciador de Dependências**: `uv` (`pyproject.toml` / `uv.lock`).

---

## 📂 Mapeamento de Pastas

*   **`agents/`**: Hub central com `MasterOrchestrator`, `AutoSkillRouter` e subagentes especialistas em `agents/specialized/`. Sem ponto de entrada em produção ainda — a camada de serviço (API Gateway/MCP) foi removida (ver nota abaixo).
*   **`skills/`**: Catálogo governado de habilidades modulares com progressive disclosure (`SKILL.md`).
*   **`shared/`**: Módulos transversais de resiliência (`circuit_breaker.py`), banco SQLite WAL (`state_orchestrator.py`), observabilidade (`logger.py`) e autenticação GCP/Workspace.
*   **`configs/`**: Políticas de segurança (`guardrails.yaml`), manifesto de agentes (`agents_manifest.yaml`) e ambiente (`.env`).
*   **`projects/`**: Aplicações clientes (`pcm`, `canvas_ide`, `keepdocs-workspace`, `customer_issue_reviewer_go`).
*   **`tests/`**: Testes automatizados unitários, de integração e avaliação.

---

## 🚀 Comandos Rápidos de Execução

Executados a partir da raiz de `meu-workspace-global` via **PowerShell**:

*   **Executar Suíte de Testes**:
    ```powershell
    uv run pytest
    ```
*   **Executar Auditoria de Qualidade & Linter**:
    ```powershell
    uv run ruff check .
    ```
*   **Auditar Catálogo de Skills**:
    ```powershell
    uv run python skills/skill_healthcheck.py
    ```

---

## 🛡️ Guardrails e Convenções

1. **Sempre responder em Português BR**.
2. **Zero-Trust & HITL**: Operações destrutivas requerem confirmação explícita conforme `configs/guardrails.yaml`.
3. **Manutenção de Tipagem**: Python 3.11+ com tipagem moderna e tratamento explícito de exceções.
4. **Prevenção de Bulk Loading de Skills**: Nunca carregar skills operacionais em bloco no orquestrador raiz. Utilizar roteamento semântico (`order-request-router`) e delegar a execução para subagentes com subcatálogos isolados.
5. **Orçamento de Contexto Estrito**: Limitar matching de progressive disclosure a no máximo 2 skills contextuais simultâneas.
