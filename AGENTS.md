# AGENTS.md — Instruções do Projeto

## Visão Geral

Repositório global de agentes autônomos, catálogo hierárquico de skills (`SKILL.md`), motores de orquestração cognitiva (`AutoSkillRouter`, `ResilienceCircuitBreaker`, `SkillHealthChecker`, `SkillFactory`, `StateOrchestrator`) e servidores FastMCP.
Arquitetura completa em `docs/architecture.md`. Idioma do projeto: **Português (BR)** — código, comentários, commits e documentação seguem pt-BR.

## Estrutura

- `agents/` — hub de agentes e orquestração:
  - `orchestrator.py`: `MasterOrchestrator` stateful integrado ao Gemini Interactions API, com guardrails Zero-Trust e persistência transacional.
  - `router.py`: `AutoSkillRouter` determinístico com classificação de complexidade e portão de segurança destrutivo.
  - `antigravity_bridge.py`: Ponte nativa com o Google Antigravity SDK.
  - `api_gateway.py`: API Gateway FastAPI com endpoints REST e SSE Streaming (`/chat`, `/chat/stream`, `/skills/health`, `/skills/create`).
  - `specialized/`: Subagentes stateless (`security_guard`, `sql_specialist`, `workspace_specialist`, `html_modular_specialist`, `research_evolution_specialist`).
- `skills/` — catálogo governado de habilidades consumido pelo `skill_parser.py` (progressive disclosure) e validado pelo `skill_healthcheck.py`, organizado em bundles:
  - `governanca/` (`resilience-circuit-breaker`, `skill-factory`, `skill-healthcheck`, `skill-context-sentinel-state`, `skill-requirements-analyzer`, `validacao-pre-entrega`, `aprimoramento-expansibilidade-agentes-skills`)
  - `auditoria/` (`code-validator`, `skill-repo-analyser`, `api-auditor`, `code-reviewer`)
  - `research/` (`deep-research`, `notebooklm`)
  - `analytics/` (`workspace-data-analytics-architect`)
  - `arquitetura/` (`project-enhancer-brainstorm`, `arquitetura-design-implementacao-sistema`)
  - `engenharia/` (`mcp-troubleshooter-design-advisor`)
  - `ui-engineering/` (`frontend-design`, `accessibility`, `tactile-hyperreal-ui-auditor`, `color-palette-and-depth-architect`, `minimal-ui-menu-icon-architect`, `responsive-html-ui-master`, `design-interface-medica-minimalista`, `skill-html-modular-builder`)
  - Standalone: `skill-prompt-generator`, `check-updates`
- `mcp_servers/` — servidor FastMCP unificado (stdio/SSE) e tools em `tools/` (BigQuery Analytics, Google Workspace, Calendar, Cloud Storage).
- `shared/` — motores utilitários:
  - `circuit_breaker.py`: Sentinela de resiliência e disjuntor de deadlocks/loops.
  - `state_orchestrator.py`: Persistência transacional com SQLite WAL em `shared/state/sessions.db`.
  - `auth/`: Autenticação para GCP Service Account / ADC (`gcp_auth.py`) e Google Workspace OAuth 2.0 com Refresh Token permanente (`workspace_auth.py`).
  - `logger.py`, `context_utils.py`.
- `configs/` — `guardrails.yaml` (lido pelo `SecurityGuardAgent`), `agents_manifest.yaml`, `.env.example`.
- `projects/` — aplicações standalone: `canvas_ide`, `customer_issue_reviewer_go`, `pcm` e `keepdocs-workspace`.
- `inbox/` — quarentena/triagem; **não é código governado** (excluída do lint).
- `tests/` — `unit/`, `integration/`, `eval/`.

## Comandos

Windows (PowerShell): `.\run.ps1 <cmd>` — Linux/macOS: `make <cmd>`

- `setup` — instala dependências (`pip install -e ".[dev]"`) e npm dos projetos.
- `dev` — sobe API Gateway (8000) + MCP SSE (8080).
- `test` — `pytest tests -v --tb=short` (todas as suítes devem passar antes de qualquer commit).
- `lint` — `ruff check .` (deve sair limpo).

## Convenções

- Python 3.11+, line-length 100, tipagem moderna (`dict[str, Any]`, `X | None`).
- Ruff: código vendorado/legado está em `extend-exclude` no `pyproject.toml` (`skills/research/notebooklm`, `inbox`, `.agents`) — não "corrigir" esses diretórios.
- Padrões de bloqueio de segurança vivem em `configs/guardrails.yaml`, **não** hardcoded.
- Novos símbolos públicos de `shared/` devem ser registrados na fachada lazy em `shared/__init__.py`, preservando imports existentes sem carregamento eager.
- `except Exception` só com `# noqa: BLE001` e justificativa (fallback proposital).
- Mudanças em estrutura/convenções → atualizar este AGENTS.md e o `README.md`.

## Segurança

- `.env` e credenciais **nunca** são versionados (ver `.gitignore`).
- Conectores MCP (`google_workspace`, `bigquery_analytics`) operam em modo híbrido real via projeto GCP `agent-md-506215` e OAuth 2.0 quando configurados, mantendo fallback simulado automático quando offline.
- Operações destrutivas exigem confirmação explícita (HITL), conforme `configs/guardrails.yaml` e `AutoSkillRouter`.
