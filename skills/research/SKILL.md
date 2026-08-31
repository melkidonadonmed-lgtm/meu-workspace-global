---
name: research
version: 1.0.0
description: Hub de pesquisa e recuperação de informação fundamentada com citações. Ponto de entrada para as sub-skills deep-research (pesquisa web multi-fonte com sub-agentes) e notebooklm (consulta aos cadernos NotebookLM do usuário).
has-sub-skill: true
triggers:
  - "pesquise sobre"
  - "deep dive"
  - "consulte meus cadernos"
  - "análise de cenário"
---

# Research — Hub de Pesquisa

Bundle de habilidades de pesquisa e recuperação de informação. Ambas as filhas produzem respostas fundamentadas com citações e são frequentemente encadeadas.

## Sub-skills

| Sub-skill | Quando usar |
|---|---|
| [`deep-research`](deep-research/SKILL.md) | Pesquisa ampla na web aberta: mercado, domínio, técnica, competitiva, acadêmica, financeira, legal etc. Relatório citado em Markdown. |
| [`notebooklm`](notebooklm/SKILL.md) | Consulta source-grounded aos cadernos NotebookLM do usuário (documentos privados), via automação de navegador. |

## Como rotear

- Fonte pública/web → `deep-research`.
- Documentos do usuário no NotebookLM → `notebooklm`.
- Pergunta que exige cruzar web aberta com documentos privados → encadear as duas, citando a origem de cada evidência.
