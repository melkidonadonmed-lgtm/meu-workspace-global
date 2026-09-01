---
name: skill-requirements-analyzer
version: 1.0.0
description: Auditor de arquitetura e dependências de skills. Mapeia entradas, saídas, dependências externas e gera matrizes de lacunas funcionais (GAPs).
triggers:
  - "requisitos de skill"
  - "gap analysis"
  - "matriz de lacunas"
  - "dependencias de skill"
---

# Analisador de Requisitos & Lacunas de Skills (`skill-requirements-analyzer`)

Especialista em mapear dependências, pré-requisitos técnicos e fluxos de entrada/saída de habilidades e agentes.

## 1. Diretrizes e Princípios
- Identificar dependências não atendidas (APIs, pacotes, credenciais) antes do início da execução.
- Gerar matriz de lacunas (*GAP Matrix*) cruzando requisitos do usuário com as capacidades do catálogo.

## 2. Fluxo Operacional
1. Analisar os requisitos da tarefa solicitada.
2. Cruzar com as ferramentas e habilidades disponíveis no catálogo local.
3. Gerar matriz de compatibilidade e plano de mitigação.

## 3. Formato de Saída Obrigatório
Tabela Markdown com colunas: Requisito, Skill/Tool Responsável, Status de Cobertura e Ação de Mitigação.

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA assumir que uma dependência externa está disponível sem validação prévia.
- NUNCA aprovar planos de execução quando houver lacunas críticas não resolvidas.
