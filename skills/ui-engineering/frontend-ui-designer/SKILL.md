---
name: frontend-ui-designer
description: Projetista e desenvolvedor de interfaces front-end de alta fidelidade. Use quando precisar criar, refatorar ou auditar layouts web/mobile, componentes de UI, sistemas de design tokens, animações CSS e páginas completas com foco em acessibilidade e responsividade.
triggers:
  - "frontend ui designer"
  - "designer ui"
  - "prototipagem"
  - "componente visual"
  - "mockup ui"
---

# Frontend UI/UX Designer Skill

Esta skill orienta a concepção estética e a codificação de interfaces modernas, funcionais e acessíveis.

## 1. Princípios de Design e Arquitetura
- **Hierarquia Visual e Tipografia:** Estabeleça contraste claro usando escalas modulares para tipografia (`rem`) e espaçamento (`gap`, `padding`, `margin`).
- **Design Tokens:** Centralize variáveis de cores (tokens semânticos: `surface`, `primary`, `on-surface`, etc.), bordas, sombras e raios via CSS Custom Properties ou Tailwind config.
- **Acessibilidade (WCAG 2.1 AA):** Garanta contraste mínimo de texto (4.5:1 para texto normal), estados de foco visíveis (`:focus-visible`), tags semânticas (`<nav>`, `<main>`, `<header>`) e atributos `aria-*` adequados.
- **Responsividade Real:** Abordagem Mobile-First, utilizando CSS Grid, Flexbox e unidades fluidas (`clamp()`, `min()`, `max()`) sem depender exclusivamente de media queries rígidas.
- **Divisão de Escopo (Hand-off):**
  - Use `frontend-ui-designer` para **construir, codificar e estilizar** componentes de UI e layouts completos.
  - Recorra a `mcp-troubleshooter-design-advisor` quando houver **falha no subagente, bloqueios de integração MCP ou necessidade de diagnóstico avançado de contraste e acessibilidade**.

---

## 2. Fluxo de Trabalho Passo a Passo

### Passo 1: Análise e Mapeamento de Requisitos
1. Identifique o público-alvo, tema visual (Clean, Brutalist, Glassmorphism, Minimalist) e suporte a Dark/Light mode.
2. Defina os componentes necessários (Navbar, Hero, Cards, Formulários, Rodapé, Modais).

### Passo 2: Estruturação dos Tokens e Layout
1. Declare a paleta de cores, tipografia e espaçamentos no escopo `:root`.
2. Estruture a marcação semântica em HTML5.

### Passo 3: Estilização e Microinterações
1. Aplique estilos responsivos com Flexbox/Grid.
2. Adicione transições suaves (`transition: all 0.2s ease-in-out`) e estados interativos (`:hover`, `:active`, `:focus-visible`, `:disabled`).

### Passo 4: Validação de Qualidade
- O layout quebra em telas menores que 360px?
- Os elementos interativos possuem área de clique mínima de 44x44px?
- Não há dependências desnecessárias ou código órfão?

---

## 3. Diretrizes de Código e Saída
- Entregue arquivos completos (`index.html`, `styles.css` e `app.js` ou componentes React/Tailwind/Vue equivalentes).
- Comente blocos não óbvios (ex: cálculos de `clamp()` ou regras de grid complexas).
- Evite placeholders como `/* restante do estilo aqui */`.

---

## 4. O que NÃO Fazer
- Não use estilos inline fixos para layout principal.
- Não remova contornos de foco (`outline: none`) sem fornecer um substituto visual explícito.
- Não use imagens pesadas ou sem atributos `alt` descritivos.
