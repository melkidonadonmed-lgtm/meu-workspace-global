---
name: notebooklm
version: 1.0.0
description: Integração de cadernos de notas, síntese cruzada de fontes documentais e suporte a Audio Overviews via Google NotebookLM.
triggers:
  - "notebooklm"
  - "audio overview"
  - "consultar notas"
  - "caderno notebooklm"
  - "síntese documental"
  - "pesquisa em notas"
---

# NotebookLM — Integração de Cadernos & Síntese Documental

Habilidade governada para consulta, extração e síntese de cadernos de notas e documentos fontes via Google NotebookLM, permitindo contextualização fundamentada e geração de Audio Overviews estruturados.

## 1. Diretrizes e Princípios

1. **Fundamentação Estrita (Groundedness):** Toda síntese e resposta gerada deve se basear exclusivamente em evidências extraídas das fontes documentais conectadas aos cadernos.
2. **Citações Precisas:** Indicar a fonte, documento ou nota de origem para cada afirmação técnica relevante.
3. **Escopo de Projetos:** Pesquisas e documentos associados devem focar nas regras e especificações dos projetos em `projects/*` (ex: documentação técnica do PCM, especificações do Canvas IDE).
4. **Isolamento de Segurança:** Proibido expor notas confidenciais ou dados de PII em respostas sem sanitização prévia.

## 2. Fluxo Operacional Passo a Passo

1. **Identificação do Caderno/Tópico:** Localizar os cadernos de estudo ou fontes documentais pertinentes à solicitação do usuário.
2. **Extração de Citações e Fatos:** Realizar consultas cruzadas entre fontes primárias (PDFs, docs, anotações de código).
3. **Síntese Técnica e Estruturação:** Consolidar os principais achados em tópicos coerentes com links para as fontes.
4. **Geração de Roteiro / Audio Overview:** Quando solicitado, formatar um roteiro em duas vozes (deep dive conversacional) para áudio explicativo.

## 3. Formato de Saída Obrigatório

Toda resposta gerada por esta skill deve conter:
- **Resumo Executivo das Notas:** Síntese em 3 a 5 pontos centrais.
- **Tabela de Fontes Consultadas:** Relação de documentos e trechos relevantes.
- **Síntese Temática Detalhada:** Explicação fundamentada das conclusões.
- **Roteiro de Audio Overview (opcional):** Script com alternância de interlocutores para podcast conceitual.

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)

- **NUNCA inventar dados ou alucinar fatos não suportados pelas notas:** Se o caderno não cobrir o tema solicitado, informar claramente a lacuna.
- **NUNCA realizar varreduras de documentos sobre a raiz do meta-workspace ou sobre a pasta de agentes (`agents/`):** O escopo documental restringe-se a documentações de projetos em `projects/*` ou fontes externas fornecidas.
- **NUNCA exportar ou vazar credenciais ou chaves de acesso a cadernos:** Chaves e tokens devem ser redigidos conforme os guardrails Zero-Trust.
