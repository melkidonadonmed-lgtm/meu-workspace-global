# 🌐 GEMINI.md — Instruções do Workspace Global de Agentes

> Este arquivo fornece as instruções operacionais e contexto para o **Gemini CLI** e o **Google Antigravity (AGY)** ao trabalhar dentro do repositório `meu-workspace-global`. Para a especificação detalhada de arquitetura e catálogo de subagentes, consulte também [AGENTS.md](file:///C:/Users/melki/meu-workspace-global/AGENTS.md).

---

## 🏛️ Visão Geral do Projeto

Repositório global de agentes autônomos, catálogo hierárquico de skills (`SKILL.md`), motores de orquestração cognitiva (`AutoSkillRouter`, `ResilienceCircuitBreaker`, `SkillHealthChecker`, `SkillFactory`, `StateOrchestrator`) e servidores FastMCP.

*   **Idioma Oficial**: Português (BR) para código, documentação, commits e respostas.
*   **Gerenciador de Dependências**: `uv` (`pyproject.toml` / `uv.lock`).

---

## 📂 Mapeamento de Pastas

*   **`agents/`**: Hub central com `MasterOrchestrator`, `AutoSkillRouter`, `AntigravityBridge`, API Gateway (`FastAPI`) e subagentes especialistas em `agents/specialized/`.
*   **`skills/`**: Catálogo governado de habilidades modulares com progressive disclosure (`SKILL.md`).
*   **`mcp_servers/`**: Servidor unificado FastMCP (stdio na porta padrão ou SSE na porta 8080).
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
*   **Iniciar API Gateway + MCP SSE**:
    ```powershell
    .\run.ps1 dev
    ```

---

## 🛡️ Guardrails e Convenções

1. **Sempre responder em Português BR**.
2. **Zero-Trust & HITL**: Operações destrutivas requerem confirmação explícita conforme `configs/guardrails.yaml`.
3. **Manutenção de Tipagem**: Python 3.11+ com tipagem moderna e tratamento explícito de exceções.
