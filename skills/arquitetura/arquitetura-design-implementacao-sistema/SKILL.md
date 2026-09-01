---
name: arquitetura-design-implementacao-sistema
version: 1.0.0
description: Design de navegabilidade e fluxo de telas, diagramas de arquitetura Mermaid e especificação funcional rigorosa dos 4 estados de interface.
triggers:
  - "diagrama mermaid"
  - "fluxo de navegabilidade"
  - "especificacao de telas"
  - "4 estados de interface"
---

# Arquitetura, Design & Implementação de Sistemas (`arquitetura-design-implementacao-sistema`)

Especialista em mapear a arquitetura lógica, diagramas conceituais e contratos de interface de aplicações web e agentes.

## 1. Diretrizes e Princípios
- Toda interface deve mapear explicitamente os **4 estados fundamentais**:
  1. **Loading:** Estado de carregamento e esqueletos visuais.
  2. **Empty:** Estado sem dados com orientação acionável ao usuário.
  3. **Success / Content:** Estado normal com dados e interação ativa.
  4. **Error:** Estado defensivo de falha com opção de retry.
- Utilizar diagramas Mermaid padronizados para visualização de grafos e sequências.

## 2. Fluxo Operacional
1. Modelar entidades e fluxos de dados.
2. Gerar diagramas Mermaid representativos.
3. Especificar os 4 estados de cada componente de tela.

## 3. Formato de Saída Obrigatório
Diagrama Mermaid (`graph TD` ou `sequenceDiagram`) acompanhado da especificação detalhada de estados.

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA omitir o tratamento de estados de erro e carregamento na especificação.
- NUNCA gerar diagramas Mermaid com sintaxes inválidas ou sem aspas em nós com caracteres especiais.
