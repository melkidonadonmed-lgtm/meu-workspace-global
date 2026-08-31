# AGENTS.md — Instruções do Projeto

## Visão Geral

Repositório global de agentes autônomos, catálogo de skills (`SKILL.md`) e servidores FastMCP.
Arquitetura completa em `docs/architecture.md`. Idioma do projeto: **Português (BR)** — código, comentários, commits e documentação seguem pt-BR.

## Estrutura

- `agents/` — hub de agentes: `orchestrator.py` (stateful, Gemini), `api_gateway.py` (FastAPI/SSE), `specialized/` (stateless)
- `skills/` — catálogo de skills consumido pelo `skill_parser.py` (progressive disclosure), organizado em bundles de sub-skills: `research/` (deep-research, notebooklm), `ui-engineering/` (frontend-design, accessibility), `auditoria/` (code-validator, skill-repo-analyser); standalone: `skill-prompt-generator`, `check-updates`
- `mcp_servers/` — servidor FastMCP unificado (stdio/SSE) e tools em `tools/`
- `shared/` — utilitários comuns (logger, contexto/tokens)
- `configs/` — `guardrails.yaml` (lido pelo `SecurityGuardAgent`), `agents_manifest.yaml`, `.env.example`
- `projects/` — frontends standalone (ex.: `canvas_ide`, Vite + React + TS + Tailwind)
- `inbox/` — quarentena/triagem; **não é código governado** (excluída do lint)
- `tests/` — `unit/`, `integration/`, `eval/`

## Comandos

Windows (PowerShell): `.\run.ps1 <cmd>` — Linux/macOS: `make <cmd>`

- `setup` — instala deps (`pip install -e ".[dev]"`) e npm do canvas_ide
- `dev` — sobe API Gateway (8000) + MCP SSE (8080)
- `test` — `pytest tests -v --tb=short` (deve passar 8/8 antes de qualquer commit)
- `lint` — `ruff check .` (deve sair limpo)

## Convenções

- Python 3.11+, line-length 100, tipagem moderna (`dict[str, Any]`, `X | None`)
- Ruff: código vendorado/legado está em `extend-exclude` no `pyproject.toml` (`skills/research/notebooklm`, `inbox`) — não "corrigir" esses diretórios
- Padrões de bloqueio de segurança vivem em `configs/guardrails.yaml`, **não** hardcoded — o `SecurityGuardAgent` carrega de lá com fallback
- `except Exception` só com `# noqa: BLE001` e justificativa (fallback proposital)
- Mudanças em estrutura/convenções → atualizar este AGENTS.md e o `README.md`

## Segurança

- `.env` e credenciais **nunca** são versionados (ver `.gitignore`)
- Conectores MCP (`google_workspace`, `bigquery_analytics`) hoje são **mocks** com dados fixos — não assumir integração real
- Operações destrutivas exigem confirmação explícita (HITL), conforme `configs/guardrails.yaml`
