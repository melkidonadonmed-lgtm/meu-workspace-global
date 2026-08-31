---
name: skill-prompt-generator
version: 1.1.0
description: Meta-engenharia e estruturação de prompts declarativos com XML tags, guardrails e pensamento em cadeia para Gemini 3.
triggers:
  - "gere um prompt"
  - "meta-prompt"
  - "otimize meu prompt"
  - "crie system prompt"
---

# Meta-Prompt Generator & Persona Architect

## Objetivo
Transformar instruções informais do usuário em especificações de prompts de nível de produção com formatação em XML (`<system_instructions>`, `<context>`, `<rules>`, `<output_format>`), garantindo adesão estrita aos guardrails e maximizando o raciocínio determinístico dos modelos Gemini 3.7 Flash e Gemini 3.1 Pro.

## Diretrizes de Estruturação
1. **Tags Semânticas Explícitas:** Separe instruções, contexto e entradas não confiáveis do usuário usando tags XML bem definidas.
2. **Exemplos Few-Shot:** Inclua pelo menos dois exemplos concretos de entrada e saída esperada.
3. **Restrições Negativas:** Especifique explicitamente o que o modelo NUNCA deve fazer.
4. **Formato Determinístico de Saída:** Exija saídas em JSON Schema estrito ou Markdown estruturado.
