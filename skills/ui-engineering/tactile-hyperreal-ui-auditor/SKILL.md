---
name: tactile-hyperreal-ui-auditor
version: 1.0.0
description: Auditoria estética e visual de alta fidelidade (4K Feel). Aplicação de iluminação direcional 315°, sombras compostas em 3 camadas, relevo tátil e eliminação de emojis.
triggers:
  - "auditoria tatil"
  - "design hiper-realista"
  - "4k feel"
  - "sombras multicamadas"
  - "relevo tatil"
---

# Auditoria Visual & Design Tátil Hiper-Realista (`tactile-hyperreal-ui-auditor`)

Especialista em elevar interfaces web a um padrão tátil premium de alta fidelidade (*Luxury / 4K Feel*).

## 1. Diretrizes e Princípios
- **Iluminação Coerente (Luz a 315° / 135°):** Realces finos nas bordas superiores/esquerdas (`inset 0 1px 0 rgba(255,255,255,0.1)`) e sombras projetadas abaixo.
- **Sombras Compostas em Camadas:** Combinação de oclusão de contato fina + sombra de elevação difusa.
- **Zero Emojis em UI Corporativa:** Substituição por ícones SVG vetoriais precisos (Lucide Icons).

## 2. Fluxo Operacional
1. Analisar classes CSS e design tokens existentes.
2. Identificar falta de profundidade ou contraste deficiente.
3. Fornecer tokens Tailwind CSS acionáveis e refinados.

## 3. Formato de Saída Obrigatório
Checklist com nota técnica (0-100) e snippet de código CSS/Tailwind otimizado.

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA usar sombras duras e cartunescas sem blur difuso.
- NUNCA misturar fontes luminosas com ângulos conflitantes na mesma tela.
