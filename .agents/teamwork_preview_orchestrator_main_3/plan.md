# Plano de Execução — Code Intelligence Agent

## Objetivo
Construir um sistema autônomo de inteligência e engenharia de código em `projects/code_intelligence_agent` integrando Google ADK e Antigravity SDK, com guardrails rigorosos de segurança, ferramentas determinísticas e suíte completa de avaliação automatizada Quality Flywheel.

## Fases de Execução

### Fase 0: Survey & Mapeamento de Escopo (3 Explorers Paralelos)
- Explorer 1: Mapeamento de SDKs, dependências ADK/Antigravity e estrutura Python/uv.
- Explorer 2: Mapeamento de ferramentas determinísticas de análise de código e guardrails de segurança (HITL, hooks, sanitização).
- Explorer 3: Mapeamento do Quality Flywheel (datasets de eval multi-turn, métricas, relatórios JSON/HTML).

### Fase 1: Arquitetura & PROJECT.md
- Síntese dos achados dos Explorers.
- Criação de `PROJECT.md` em `projects/code_intelligence_agent/PROJECT.md` com arquitetura, contratos e inventário de features.

### Fase 2: Ciclos de Implementação & Verificação
- M1: Scaffold do Projeto, pyproject.toml, estrutura de pacotes e infraestrutura de testes.
- M2: Motor Central de Inteligência de Código, Ferramentas Determinísticas e Memória Conversacional.
- M3: Guardrails de Segurança, Interceptadores de Ciclo de Vida (HITL, sanitização SO, fronteiras).
- M4: Interfaces CLI e Servidor FastAPI / ADK API Server.
- M5: Suíte Quality Flywheel (`tests/eval/`), datasets multi-turn, `eval_config.yaml`, runner e relatórios.

### Fase 3: Validação Integrada & Gate Final
- Execução de 100% dos testes via pytest e linter ruff limpo.
- Execução do Quality Flywheel com métricas validadas:
  - `multi_turn_task_success >= 0.85`
  - `multi_turn_tool_use_quality >= 0.80`
- Relatórios `results_*.json` e `.html` gerados.
- Handoff para o Sentinela para acionamento da Victory Audit.
