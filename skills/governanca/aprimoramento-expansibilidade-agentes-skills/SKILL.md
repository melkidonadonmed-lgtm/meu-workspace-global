---
name: aprimoramento-expansibilidade-agentes-skills
version: 1.1.0
description: Engenharia de Contexto de Alta Fidelidade — 5 Pilares (Negative Bounds, Shumer Method, Escalation Ladder, Budgeted Context, 4 Blocos XML) para diagnóstico, refatoração e blindagem de agentes, subagentes e SKILL.md.
triggers:
  - "engenharia de contexto"
  - "context engineering"
  - "budgeted context"
  - "shumer method"
  - "negative bounds"
  - "escalonamento de prompt"
  - "context rot"
  - "expansibilidade de agentes"
references:
  - references/pilares-detalhados.md
---

# Aprimoramento, Engenharia de Contexto & Expansibilidade de Agentes (`aprimoramento-expansibilidade-agentes-skills`)

Especialista em Context Engineering: previne degradação de contexto (*context rot*), governa orçamento de tokens e blinda agentes autônomos. Use quando for **auditar, refatorar ou criar** um agente, subagente ou `SKILL.md`.

> Detalhamento completo (templates, tabela de escalonamento, exemplo XML, diagrama de fluxo) está em `references/pilares-detalhados.md` — carregar sob demanda, não inline por padrão.

## 1. Os 5 Pilares (resumo)

1. **Negative Prompting & Whitelisting Estrito** — toda instrução de agente deve declarar Zonas de Não-Ação explícitas e restringir ferramentas a um schema fechado.
2. **Shumer Method (decisão em 4 ângulos)** — Recomendação Direta, Fatores Determinantes, Contra-argumento Mais Forte, O que Mudaria a Decisão.
3. **Escalation Ladder** — Zero-Shot+Schema → Few-Shot → Chain-of-Thought → Agente com Tools; nunca escale além do necessário.
4. **Budgeted Context Assembly** — 5 cotas de token: Sistema 15% / Estado 15% / Tools 20% / Dados 40% / Margem 10%.
5. **4 Blocos XML** — todo contexto injetado em subagentes deve ser modularizado em `<identidade>`, `<estado_atual>`, `<habilidades_ativas>`, `<dados_trabalho>`.

## 2. Fluxo Operacional (resumo)

1. Auditar volume: se instruções estáticas > 1.500 tokens, segregar em `references/` (Progressive Disclosure).
2. Inserir Negative Bounds explícitas.
3. Calibrar complexidade pela Escalation Ladder.
4. Estruturar contexto nos 4 Blocos XML.
5. Fechar com ciclo Self-Refine antes da entrega final.

## 3. Formato de Saída Obrigatório

Toda auditoria/refatoração emite 4 seções: Diagnóstico de Engenharia de Contexto, Análise Crítica (Shumer Method), Artefato Refatorado e Blindado, Ganhos Quantitativos Esperados. Template completo em `references/pilares-detalhados.md`.

## 4. Zonas de Não-Ação (Negative Bounds)

- NUNCA crie mega-prompts monolíticos sem segregar estado e dados de trabalho em tags XML.
- NUNCA delegue tarefas simples (Nível 1-2) a cadeias multiagente complexas — respeite a Escalation Ladder.
- NUNCA deixe um agente autônomo sem Zonas de Não-Ação explícitas e critérios de parada.
- NUNCA misture instruções de sistema e dados de entrada brutos no mesmo nível hierárquico.
- NUNCA execute refatorações sem validar o resultado via `validate_skill.py`.
- NUNCA ultrapasse a cota de 1.500 tokens de instrução estática sem mover o excedente para `references/`.
