---
name: auditoria
version: 1.0.0
description: Hub de análise pré-mudança. Ponto de entrada para as sub-skills code-validator (auditoria de código com matriz de risco percentual) e skill-repo-analyser (varredura e reorganização estrutural de repositórios). Todas emitem relatório e exigem aprovação antes de aplicar mudanças.
has-sub-skill: true
triggers:
  - "audite"
  - "analise o risco"
  - "reorganize meu repositório"
  - "valide este código"
---

# Auditoria — Hub de Análise Pré-Mudança

Bundle de habilidades que seguem o mesmo fluxo: **varrer → mapear riscos/conflitos → relatório estruturado → aprovação humana (HITL) antes de qualquer aplicação**.

## Sub-skills

| Sub-skill | Quando usar |
|---|---|
| [`code-validator`](code-validator/SKILL.md) | Auditoria de código-fonte (macro ao micro, linha a linha), expansão de contexto e matriz de risco percentual com justificativa causal. |
| [`skill-repo-analyser`](skill-repo-analyser/SKILL.md) | Varredura de pastas soltas, mapeamento de dependências/redundâncias e plano de montagem de repositório global. |

## Como rotear

- Risco de um trecho/base de código → `code-validator`.
- Estrutura de diretórios e organização do workspace → `skill-repo-analyser`.
- Reorganização grande que toca código → encadear: `skill-repo-analyser` para o plano estrutural, `code-validator` para o risco dos módulos afetados.
