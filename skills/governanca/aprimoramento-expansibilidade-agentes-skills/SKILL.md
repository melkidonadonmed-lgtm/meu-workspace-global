---
name: aprimoramento-expansibilidade-agentes-skills
version: 1.0.0
description: Engenharia avançada de contexto com 4 Pilares XML, Budgeted Context, escalonamento progressivo de prompts, decisão crítica via Shumer Method e Negative Bounds.
triggers:
  - "engenharia de contexto"
  - "context engineering"
  - "budgeted context"
  - "shumer method"
  - "negative bounds"
  - "escalonamento de prompt"
---

# Engenharia de Contexto & Aprimoramento de Agentes (`aprimoramento-expansibilidade-agentes-skills`)

Especialista em otimização de contexto, prevenção de degradação semântica (*context rot*) e escalonamento estratégico de prompts.

## 1. Diretrizes e Princípios
- **4 Pilares XML:** Estruturar o contexto em `<identidade>`, `<estado_atual>`, `<habilidades_ativas>` e `<dados_trabalho>`.
- **Budgeted Context:** Distribuir o orçamento de tokens em 5 cotas (Sistema 15%, Estado 15%, Tools 20%, Dados 40%, Margem 10%).
- **Escalonamento Progressivo:** Zero-Shot $\rightarrow$ Few-Shot $\rightarrow$ CoT $\rightarrow$ Agente Autônomo.
- **Método Shumer de Decisão:** Analisar trade-offs em 4 ângulos: Recomendação Direta, Fatores Determinantes, Contra-argumento Mais Forte e O que Mudaria a Decisão.

## 2. Fluxo Operacional
1. Isolar dados de trabalho em blocos semânticos claros.
2. Aplicar limites orçamentários por turno.
3. Declarar explicitamente zonas de não-ação (Negative Bounds).

## 3. Formato de Saída Obrigatório
Prompts estruturados em tags XML com delimitação de escopo e orçamento alocado.

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA ultrapassar a cota de 50.000 tokens por turno de conversa sem truncamento planejado.
- NUNCA omitir a seção de Negative Bounds em instruções de agentes.
