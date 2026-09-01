---
name: governanca
version: 1.0.0
description: Hub de governança, resiliência, criação e auditoria de habilidades e agentes autônomos no ecossistema global.
has-sub-skill: true
triggers:
  - "governanca"
  - "circuit breaker"
  - "disjuntor"
  - "saude do catalogo"
  - "criar skill"
  - "validar entrega"
  - "context sentinel"
---

# Governança & Resiliência — Hub de Integridade do Ecossistema

Bundle responsável pela proteção operacional, resiliência contra loops, auditoria de integridade, engenharia de contexto e evolução do catálogo de skills.

## Sub-skills

| Sub-skill | Quando usar |
|---|---|
| [`resilience-circuit-breaker`](resilience-circuit-breaker/SKILL.md) | Disjuntor determinístico contra loops infinitos, deadlocks e controle de cota de tokens. |
| [`skill-factory`](skill-factory/SKILL.md) | Fabricação e padronização de novas habilidades no formato canônico SKILL.md. |
| [`skill-healthcheck`](skill-healthcheck/SKILL.md) | Auditoria de integridade sintática, coerência de nomes e redundâncias do catálogo. |
| [`skill-context-sentinel-state`](skill-context-sentinel-state/SKILL.md) | Auditoria periódica da janela de contexto e compilação de snapshots de estado a cada 5 turnos. |
| [`skill-requirements-analyzer`](skill-requirements-analyzer/SKILL.md) | Auditoria de dependências, mapeamento de entradas/saídas e matrizes de lacunas (GAPs). |
| [`validacao-pre-entrega`](validacao-pre-entrega/SKILL.md) | Protocolo de validação dimensional (4 eixos) com cálculo de ganho percentual ($\Delta\%$) e score 0–100. |
| [`aprimoramento-expansibilidade-agentes-skills`](aprimoramento-expansibilidade-agentes-skills/SKILL.md) | Engenharia de contexto avançada (4 Pilares XML, Budgeted Context, Escalonamento de Prompts). |

## Zonas de Não-Ação & O que NÃO Fazer
- NUNCA desabilitar guardrails ou disjuntores em tempo de execução sem autorização humana (HITL).
- NUNCA finalizar criação de skills sem validação estrutural prévia.
- NUNCA permitir degradação de contexto (*context rot*) sem disparar snapshot de estado.
