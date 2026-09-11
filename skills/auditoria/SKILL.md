---
name: auditoria
version: 1.0.0
description: Hub de análise pré-mudança. Ponto de entrada para as sub-skills code-validator, skill-repo-analyser, api-auditor e code-reviewer. Todas emitem relatório e exigem aprovação antes de aplicar mudanças.
has-sub-skill: true
triggers:
  - "audite"
  - "analise o risco"
  - "reorganize meu repositório"
  - "valide este código"
  - "check"
  - "test"
  - "audit"
  - "review"
---

# Auditoria — Hub de Análise Pré-Mudança

Bundle de habilidades que seguem o mesmo fluxo: **varrer → mapear riscos/conflitos → relatório estruturado → aprovação humana (HITL) antes de qualquer aplicação**.

## Sub-skills

| Sub-skill | Quando usar |
|---|---|
| [`code-validator`](code-validator/SKILL.md) | Auditoria de código-fonte (macro ao micro, linha a linha), expansão de contexto e matriz de risco percentual com justificativa causal. |
| [`skill-repo-analyser`](skill-repo-analyser/SKILL.md) | Varredura de pastas soltas, mapeamento de dependências/redundâncias e plano de montagem de repositório global. |
| [`api-auditor`](api-auditor/SKILL.md) | Auditoria e testes de endpoints de API e URLs para verificação de integridade e latência. |
| [`code-reviewer`](code-reviewer/SKILL.md) | Revisão automatizada de arquivos e alterações de código para checagem de qualidade. |
| [`web-security-auditor`](web-security-auditor/SKILL.md) | Checklist e auditoria sistemática de segurança para Web Apps (OWASP, injeções, segredos, headers). |

## Como rotear

- Risco de um trecho/base de código → `code-validator`.
- Estrutura de diretórios e organização do workspace → `skill-repo-analyser`.
- Teste de endpoint de API ou URL → `api-auditor`.
- Revisão de arquivo ou alterações de código para qualidade/estilo → `code-reviewer`.
- Auditoria de segurança web, segredos, auth ou headers → `web-security-auditor`.
- Reorganização grande que toca código → encadear: `skill-repo-analyser` para o plano estrutural, `code-validator` para o risco dos módulos afetados.
- Auditoria de bloating de contexto ou ativação incorreta de skills em bloco → avaliar conformidade com o padrão Root Agent e isolamento de `AGENT_SUBCATALOGS`.

## Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)

- **NUNCA executar auditorias sobre o meta-workspace ou a pasta de agentes:** As habilidades deste bundle destinam-se exclusivamente a inspecionar e auditar projetos clientes em `projects/*` (ex: `projects/pcm`, `projects/canvas_ide`, `projects/keepdocs-workspace`).
- **NUNCA executar auto-auditoria sobre a raiz (`.` ou `meu-workspace-global`), sobre `agents/` ou sobre `skills/`:** Qualquer instrução ou rotina que mire esses caminhos de infraestrutura do sistema deve ser terminantemente rejeitada sob o guardrail de fronteira (`AUDIT_TARGET_PROHIBITED`).

