---
name: deep-research-hub
version: 1.0.0
description: Hub de pesquisa aprofundada, síntese em fontes primárias e investigação técnica multidisciplinar.
has-sub-skill: true
triggers:
  - "pesquisa profunda"
  - "deep research"
  - "analise de mercado"
---

# Research — Hub de Pesquisa e Investigação Técnica

Bundle responsável por investigações aprofundadas, varreduras na web com validação multi-fonte e compilação de relatórios técnicos fundamentados com citações.

## Sub-skills

| Sub-skill | Quando usar |
|---|---|
| [`deep-research`](deep-research/SKILL.md) | Pesquisa aprofundada multi-fonte na web aberta cobrindo 11 modalidades (mercado, técnica, competitiva, produto, acadêmica, financeira, legal, tendências, pessoas/organizações, comunidade e domínio). |
| [`notebooklm`](notebooklm/SKILL.md) | Integração de cadernos de notas, síntese cruzada de fontes documentais e suporte a Audio Overviews via Google NotebookLM. |

## Como Rotear

- **Pesquisa Aprofundada / Estado da Arte**: Acionar `deep-research` para investigações técnicas, análises de mercado, benchmarks competitivos e levantamentos estruturados com citações.
- **Roteamento e Contexto**: Demandas de pesquisa profunda e consulta a cadernos são executadas em sessões dedicadas com progressive disclosure (top-k <= 2), preservando o contexto operacional do agente raiz.
- **Modos de Pesquisa**:
  - `Quick`: Perguntas pontuais e rápidas (Passos 1, 2 e 5).
  - `Standard`: Pesquisa aprofundada típica com multi-fontes e síntese (Passos 1 a 5).
  - `Deep`: Análise exaustiva para decisões críticas com refinamento e critique pass.

## O que NÃO Fazer (Negative Bounds)

- NUNCA inventar fontes ou URLs inexistentes; toda afirmação deve possuir citação verificável.
- NUNCA assumir conclusões precipitadas sem validação cruzada entre múltiplas fontes independentes.
- NUNCA realizar mutações destrutivas no workspace durante a fase de levantamento e pesquisa.
- NUNCA carregar subcatálogos inteiros de pesquisa no agente raiz em bloco; respeitar o progressive disclosure (top-k <= 2).

