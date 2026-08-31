---
name: ui-engineering
version: 1.0.0
description: Hub de construção de interfaces. Ponto de entrada para as sub-skills frontend-design (direção visual, tipografia e layout) e accessibility (requisitos de acessibilidade para UI interativa).
has-sub-skill: true
triggers:
  - "criar interface"
  - "novo painel/view/widget"
  - "design da página"
  - "atualizar UI"
---

# UI Engineering — Hub de Interface

Bundle de habilidades acionadas ao criar ou atualizar UI. As filhas são complementares: direção estética + conformidade de acessibilidade.

## Sub-skills

| Sub-skill | Quando usar |
|---|---|
| [`frontend-design`](frontend-design/SKILL.md) | Definir direção visual intencional: paleta, tipografia, layout, motion e copy. Evita aparência de template genérico. |
| [`accessibility`](accessibility/SKILL.md) | Garantir acessibilidade em superfícies interativas: help dialog, accessible view, verbosity, sinais, ARIA e navegação por teclado. Escopo atual: codebase do VS Code. |

## Como rotear

- Toda nova superfície de UI interativa → aplicar **as duas** em conjunto.
- Somente direção estética/rebranding → `frontend-design`.
- Somente conformidade/correção de a11y → `accessibility`.
