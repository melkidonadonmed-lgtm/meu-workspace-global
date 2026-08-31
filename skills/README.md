# Catálogo de Habilidades Modulares (`/skills`)

Este diretório contém a biblioteca de habilidades especializadas (*skills*) do ecossistema de agentes. Cada habilidade é autocontida em seu próprio subdiretório e declarada através de um arquivo `SKILL.md`.

## Princípio de Progressive Disclosure (Descoberta Progressiva)
Para evitar **poluição de contexto (*context bloat*)**, o orquestrador não carrega todas as instruções de todas as skills no System Prompt. Ele injeta apenas os metadados (nome e descrição resumida). O conteúdo detalhado é recuperado e injetado dinamicamente somente quando a tarefa atual demanda aquela especialidade.

## Habilidades Instaladas

| Habilidade | Versão | Descrição |
|---|---|---|
| [`skill-repo-analyser`](file:///skills/skill-repo-analyser/SKILL.md) | 2.0.0 | Inspeção, mapeamento de dependências e reorganização estrutural de workspaces. |
| [`code-validator`](file:///skills/code-validator/SKILL.md) | 1.0.0 | Auditoria de código (macro e micro), cálculo de risco percentual com rationale causal e guardrails. |
| [`skill-prompt-generator`](file:///skills/skill-prompt-generator/SKILL.md) | 1.1.0 | Engenharia e estruturação de prompts de alta fidelidade para modelos Gemini 3. |
| [`accessibility`](file:///skills/accessibility/SKILL.md) | 1.0.0 | Auditoria de acessibilidade web (WCAG 2.2, contraste, semântica ARIA). |
| [`deep-research`](file:///skills/deep-research/SKILL.md) | 1.1.0 | Fluxos de pesquisa aprofundada, síntese de evidências e consolidação bibliográfica. |
| [`frontend-design`](file:///skills/frontend-design/SKILL.md) | 1.0.0 | Arquitetura e design system para interfaces ricas, Tailwind e componentes React. |
| [`notebooklm-skill-master`](file:///skills/notebooklm-skill-master/SKILL.md) | 1.0.0 | Integração, análise e extração estruturada de cadernos e fontes NotebookLM. |
| [`check-updates`](file:///skills/check-updates/SKILL.md) | 1.0.0 | Verificação de integridade e atualizações de ferramentas e dependências. |

## Como Criar uma Nova Habilidade
1. Crie uma pasta em `skills/minha-nova-skill/`.
2. Adicione o arquivo `SKILL.md` com o cabeçalho YAML frontmatter:
```yaml
---
name: minha-nova-skill
version: 1.0.0
description: Descrição curta do que a skill faz.
triggers:
  - "palavra-chave-1"
  - "palavra-chave-2"
---

# Instruções de Execução da Skill
...
```
3. O `skill_parser.py` detectará a nova habilidade automaticamente.
