# Catálogo de Habilidades Modulares (`/skills`)

Este diretório contém a biblioteca de habilidades especializadas (*skills*) do ecossistema de agentes. Cada habilidade é autocontida em seu próprio subdiretório e declarada através de um arquivo `SKILL.md`.

Skills relacionadas são organizadas em **bundles de sub-skills**: um diretório *parent* com `has-sub-skill: true` no frontmatter atua como ponto de entrada e roteador, e cada filha vive em um subdiretório do parent. O `skill_parser.py` descobre recursivamente tanto parents quanto filhas.

## Princípio de Progressive Disclosure (Descoberta Progressiva)
Para evitar **poluição de contexto (*context bloat*)**, o orquestrador não carrega todas as instruções de todas as skills no System Prompt. Ele injeta apenas os metadados (nome e descrição resumida). O conteúdo detalhado é recuperado e injetado dinamicamente somente quando a tarefa atual demanda aquela especialidade.

## Bundles de Sub-skills

| Parent | Sub-skills | Domínio |
|---|---|---|
| [`research`](research/SKILL.md) | [`deep-research`](research/deep-research/SKILL.md), [`notebooklm`](research/notebooklm/SKILL.md) | Pesquisa fundamentada com citações (web aberta + cadernos NotebookLM). |
| [`ui-engineering`](ui-engineering/SKILL.md) | [`frontend-design`](ui-engineering/frontend-design/SKILL.md), [`accessibility`](ui-engineering/accessibility/SKILL.md) | Construção de interfaces: direção visual + acessibilidade. |
| [`auditoria`](auditoria/SKILL.md) | [`code-validator`](auditoria/code-validator/SKILL.md), [`skill-repo-analyser`](auditoria/skill-repo-analyser/SKILL.md) | Análise pré-mudança: risco de código + estrutura de repositório. |

## Habilidades Standalone

| Habilidade | Versão | Descrição |
|---|---|---|
| [`skill-prompt-generator`](skill-prompt-generator/SKILL.md) | 1.1.0 | Engenharia e estruturação de prompts de alta fidelidade para modelos Gemini 3. |
| [`check-updates`](check-updates/SKILL.md) | 1.0.0 | Verificação de integridade e atualizações de ferramentas e dependências. |

## Como Criar uma Nova Habilidade
1. Crie uma pasta em `skills/minha-nova-skill/` — ou dentro de um bundle existente (`skills/<bundle>/minha-nova-skill/`) se ela pertencer àquele domínio.
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
3. Para criar um novo bundle, adicione `has-sub-skill: true` no frontmatter do parent.
4. O `skill_parser.py` detectará a nova habilidade automaticamente.
