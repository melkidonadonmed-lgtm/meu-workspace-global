---
name: minimal-ui-menu-icon-architect
version: 1.0.0
description: Arquitetura de menus minimalistas de alta precisão (docks, sidebars retráteis, navbars) e iconografia vetorial em SVG inline sem emojis.
triggers:
  - "menu minimalista"
  - "sidebar retratil"
  - "dock menu"
  - "icones svg"
  - "navbar"
---

# Menus Minimalistas & Arquitetura de Ícones (`minimal-ui-menu-icon-architect`)

Especialista em componentes de navegação espacial, menus retráteis com microinterações fluidas e iconografia vetorial limpa.

## 1. Diretrizes e Princípios
- Menus devem respeitar ergonomia touch/click (mínimo de 44x44px de área de toque).
- Estados ativos e de foco (`focus-visible`) visualmente distintos e acessíveis por teclado.
- Ícones em SVG inline ou componentes React (Lucide Icons) com espessura de traço consistente (`stroke-width: 1.5` ou `2`).

## 2. Fluxo Operacional
1. Definir hierarquia de rotas e itens de menu.
2. Construir componente de navegação responsivo (sidebar colapsável / bottom dock).
3. Aplicar transições suaves de abertura/fechamento.

## 3. Formato de Saída Obrigatório
Código completo do componente em React/Tailwind ou HTML5/CSS3 puro, sem omissões.

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA usar emojis como substitutos de ícones de navegação em interfaces executivas.
- NUNCA criar menus que causem deslocamento de layout (*layout shift*) ao abrir ou fechar.
