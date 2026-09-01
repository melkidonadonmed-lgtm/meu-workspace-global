---
name: validacao-pre-entrega
version: 1.0.0
description: Validação dimensional de integridade, sintaxe, segurança e funcionalidade de códigos e artefatos antes do envio final com cálculo de ganho percentual.
triggers:
  - "validacao pre-entrega"
  - "validar entrega"
  - "relatorio de ganho"
  - "score dimensional"
---

# Procedimento Operacional: Validação Pré-Entrega com Métricas Dimensionais

Valida a integridade de códigos, prompts e artefatos sob 4 eixos fundamentais antes da entrega ao usuário.

## 1. Diretrizes e Matriz de Avaliação
1. **Segurança & Robustez (Peso 30%):** Ausência de segredos expostos, injeção de código e tratamento defensivo de exceções.
2. **Qualidade Técnica & Sintaxe (Peso 30%):** Código 100% funcional, ausência de placeholders, tipagem estrita e linting.
3. **Velocidade & Eficiência (Peso 20%):** Complexidade algorítmica, consumo consciente de tokens/contexto.
4. **Clareza & Usabilidade (Peso 20%):** Aderência às instruções do usuário, documentação e legibilidade.

$$\text{Score Geral} = (S \times 0.30) + (Q \times 0.30) + (V \times 0.20) + (C \times 0.20)$$

## 2. Fluxo Operacional
1. Avaliar o artefato inicial atribuindo nota de 0 a 100 para cada eixo.
2. Aplicar correções, tipagens e sanitizações.
3. Avaliar o artefato final e calcular o ganho percentual total ($\Delta\%$).

## 3. Formato de Saída Obrigatório
```text
==================================================
📊 RELATÓRIO DE VALIDAÇÃO & GANHO DE EXECUÇÃO
==================================================
• Segurança & Robustez:      [Nota Inicial]% ➔ [Nota Final]%
• Qualidade & Sintaxe:        [Nota Inicial]% ➔ [Nota Final]%
• Eficiência & Velocidade:    [Nota Inicial]% ➔ [Nota Final]%
• Clareza & Funcionalidade:   [Nota Inicial]% ➔ [Nota Final]%
--------------------------------------------------
📈 GANHO GLOBAL ESTIMADO: +[Delta Total]%
==================================================
```

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA entregar código com erros de linting ou testes falhando.
- NUNCA omitir itens corrigidos no relatório de auditoria.
