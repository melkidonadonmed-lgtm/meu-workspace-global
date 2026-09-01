---
name: analytics
version: 1.0.0
description: Hub de análise de dados, métricas tabulares, agregação de planilhas e dashboards analíticos de produtividade.
has-sub-skill: true
triggers:
  - "analytics"
  - "metricas de workspace"
  - "dashboard"
  - "dados tabulares"
---

# Analytics — Hub de Dados e Inteligência Analítica

Bundle responsável pela agregação de métricas, inteligência sobre dados do Google Workspace e geração de visualizações executivas.

## Sub-skills

| Sub-skill | Quando usar |
|---|---|
| [`workspace-data-analytics-architect`](workspace-data-analytics-architect/SKILL.md) | Painéis de produtividade, KPIs, agregação de dados tabulares e chat analítico sobre planilhas. |

## Zonas de Não-Ação & O que NÃO Fazer
- NUNCA expor dados sensíveis ou PII sem anonimização prévia.
- NUNCA executar agregações destrutivas sobre fontes primárias.
