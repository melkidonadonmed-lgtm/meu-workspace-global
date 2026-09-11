# Project: Code Intelligence & Tool Calling Agent

## Overview
Sistema autônomo de inteligência e engenharia de código para ambiente de produção em `projects/code_intelligence_agent`, integrando Google ADK 2.9.0 e Antigravity SDK, dotado de guardrails rigorosos de segurança (Zero-Trust, HITL, sanitização de PII e boundary guard), ferramentas determinísticas de análise estática e AST, interfaces CLI e FastAPI, e uma suíte completa de avaliação automatizada Quality Flywheel (`agents-cli eval`).

## Architecture
```
projects/code_intelligence_agent/
├── pyproject.toml                     # Configuração de empacotamento uv e hatchling
├── README.md                          # Guia de uso, CLI, API e arquitetura
├── .env.example                       # Modelo de variáveis de ambiente
├── app/                               # Pacote canônico do agente ADK (App name="app")
│   ├── __init__.py
│   ├── agent.py                       # Root agent, App e Runner ADK
│   ├── tools.py                       # Ferramentas determinísticas de código (AST, patch, inspeção)
│   ├── guardrails.py                  # Interceptadores de ciclo de vida e guardrails R2
│   ├── fast_api_app.py                # Servidor FastAPI e rotas ADK
│   └── cli.py                         # Interface de linha de comando CLI (code-intel)
├── artifacts/
│   └── grade_results/                 # Relatórios results_*.json e results_*.html
└── tests/
    ├── conftest.py                    # Fixtures compartilhadas e isolamento
    ├── unit/                          # Testes unitários de ferramentas e guardrails
    ├── integration/                   # Testes de integração de CLI e API
    └── eval/                          # Suíte Quality Flywheel (R3)
        ├── datasets/
        │   └── code_intelligence_multi_turn.json # Dataset canônico multi-turn
        ├── eval_config.yaml           # Configuração de métricas e thresholds
        └── eval_runner.py             # Runner automatizado dual e relatórios
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | F1: Scaffold & Packaging | `pyproject.toml` com hatchling, uv e layout `app/` | M1 | Survey E1 |
| 2 | F2: Deterministic Tools | `inspect_directory`, `read_code_file`, `analyze_ast_anomalies`, `generate_unified_patch` | M1 | Survey E2 |
| 3 | F3: ADK Agent Core & State | `root_agent` no ADK 2.9.0 com `gemini-3.8-flash` e `tool_context.state` | M1 | Survey E1 |
| 4 | F4: Security Guardrails | Boundary Guard, bloqueio de comandos destrutivos SO, redação PII/credenciais, HITL | M2 | Survey E2 |
| 5 | F5: Execution Interfaces | CLI `code-intel` e servidor FastAPI com endpoints `/healthz`, `/api/v1/analyze`, `/api/v1/query` | M3 | Survey E1 |
| 6 | F6: Multi-turn Eval Dataset | 5 cenários multi-turn canônicos em `tests/eval/datasets/code_intelligence_multi_turn.json` | M3 | Survey E3 |
| 7 | F7: Eval Config | `tests/eval/eval_config.yaml` com metas task_success >= 0.85 e tool_quality >= 0.80 | M3 | Survey E3 |
| 8 | F8: Dual Eval Runner & Reports | Runner `CodeIntelligenceEvalRunner` gerando `results_*.json` e `.html` | M3 | Survey E3 |
| 9 | F9: Complete Test Suite & Validation | 100% pytest pass com `--basetemp`, ruff clean e relatórios comprovados | M4 | Survey E1/E2/E3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Scaffold & Code Intelligence Engine | Estrutura de diretórios, pyproject.toml, ferramentas determinísticas (AST, patch, inspeção), núcleo ADK e testes unitários | None | DONE |
| 2 | M2: Security Guardrails & Interceptors (R2) | Boundary Guard, bloqueio comandos destrutivos, mascaramento PII/credenciais, callbacks ADK e testes | M1 | DONE |
| 3 | M3: Interfaces (CLI/FastAPI) & Quality Flywheel (R3) | CLI `code-intel`, FastAPI app, dataset multi-turn, eval_config.yaml, eval_runner.py e relatórios JSON/HTML | M2 | DONE |
| 4 | M4: Validação E2E, Hardening & Final Gate | Execução de 100% dos testes, ruff clean, Quality Flywheel meeting thresholds e handoff | M3 | DONE |

## Gate Results
- **M1 Gate**: PASS (34 testes passando, ruff limpo, ferramentas determinísticas com dry-run AST).
- **M2 Gate**: PASS (50 testes passando, guardrails R2 com boundary guard, bloqueio destrutivo e sanitização de PII/credenciais).
- **M3 Gate**: PASS (70 testes passando, CLI typer, FastAPI app, Quality Flywheel com 100% task success e 100% tool quality).
- **M4 Final Gate**: **PASS** (123 testes passando, 0 falhas, ruff 0 erros, auditoria forense aprovada com ZERO cheating, relatórios results_*.json e .html gerados em artifacts/grade_results/).

