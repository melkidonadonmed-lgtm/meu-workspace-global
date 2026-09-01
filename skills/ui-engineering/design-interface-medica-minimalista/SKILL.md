---
name: design-interface-medica-minimalista
version: 1.0.0
description: Padrão de UI/UX executivo para aplicações médicas e clínicas. Zero emojis, tipografia sóbria, cores Slate/Emerald, conformidade com CFM/ANVISA e impressão A4 perfeita.
triggers:
  - "ui medica"
  - "interface clinica"
  - "prontuario"
  - "receituario medico"
  - "impressao a4 medica"
---

# Design de Interfaces Médicas Minimalistas (`design-interface-medica-minimalista`)

Especialista em ergonomia, sobriedade visual e padrões técnicos para sistemas de prontuário, receituário e calculadoras clínicas.

## 1. Diretrizes e Princípios
- **Sobriedade Clínica:** Zero emojis ou ilustrações recreativas. Ícones clínicos discretos (Lucide Icons).
- **Paleta Segura:** Cores neutras (Slate/Zinc) com destaques funcionais em Emerald/Teal (saúde) e Rose/Amber (alertas clínicos).
- **Impressão A4 Perfeita:** Media queries `@media print` dedicadas, escondendo barras de navegação e garantindo que o receituário/atestado caiba em folha física padrão com margens precisas.
- **Conformidade Legal:** Campos obrigatórios alinhados com resoluções do CFM (Conselho Federal de Medicina) e ANVISA.

## 2. Fluxo Operacional
1. Modelar o formulário ou calculadora clínica com validação de doses.
2. Aplicar design system minimalista e sóbrio.
3. Configurar estilos de impressão `@media print` para exportação direta em PDF/impressora.

## 3. Formato de Saída Obrigatório
Componente React/Tailwind ou CSS com regras de impressão e visualização clínica limpa.

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA incluir emojis em interfaces médicas ou documentos emitidos para pacientes.
- NUNCA alterar doses de medicamentos sem validação contra referências farmacológicas oficiais.
