# 🎯 Guia de Referência — Como Pedir para IAs Gerarem Código (Frontend/Web)

> Um manual prático para estruturar prompts que geram resultados realmente úteis.

---

## 📋 Estrutura Básica de um Bom Pedido

Sempre que possível, inclua estas 5 camadas:

```
1. O QUE você quer      → Descrição clara do resultado final
2. PARA QUEM / POR QUÊ  → Contexto, público-alvo, objetivo
3. COMO deve parecer    → Estilo visual, referências, mood
4. COMO deve funcionar  → Interações, comportamentos, estados
5. RESTRIÇÕES           → O que NÃO pode ter, limitações técnicas
```

---

## 🏗️ Camada 1 — O Que Você Quer (Escopo)

Seja específico. Evite "faz uma página bonita".

| ❌ Ruim | ✅ Bom |
|---------|--------|
| "Faz um site de restaurante" | "Landing page de um restaurante italiano com menu interativo, formulário de reserva e seção 'Sobre o Chef'" |
| "Cria um dashboard" | "Dashboard administrativo com sidebar, cards de métricas (vendas, usuários, taxa de conversão), gráfico de linha dos últimos 30 dias e tabela de pedidos recentes" |
| "Página de login" | "Tela de login com validação em tempo real, toggle mostrar/esconder senha, link 'esqueci minha senha' e opção de login social (Google)" |

**Palavras-chave úteis:**
- `Landing page` — página única de conversão
- `Dashboard / Admin panel` — painel administrativo
- `Single Page Application (SPA)` — app de página única
- `Portfolio / Showcase` — galeria de trabalhos
- `E-commerce product page` — página de produto
- `Authentication flow` — fluxo de login/cadastro
- `CRUD interface` — criar, ler, atualizar, deletar

---

## 🎨 Camada 2 — Estilo Visual (Look & Feel)

### 2.1 Definir o "Mood" Geral

Use **referências concretas** sempre que possível:

```
"Estilo Apple — minimalista, muito whitespace, tipografia clean"
"Estilo Stripe — gradients sutis, ilustrações geométricas, dados em destaque"
"Estilo Spotify — escuro, vibrante, foco em descoberta"
"Estilo Notion — clean, funcional, sem distrações"
```

Ou descreva com adjetivos:
- **Profissional/ Corporativo:** clean, minimalista, confiável
- **Criativo/ Artístico:** bold, experimental, tipografia expressiva
- **Tecnológico/ Moderno:** futurista, dark mode, glassmorphism, neon
- **Orgânico/ Natural:** tons terrosos, bordas arredondadas, ilustrações handmade
- **Premium/ Luxo:** elegante, serifas, espaçamento generoso, dourado/preto

### 2.2 Sistema de Cores

Sempre especifique ou peça:

```
"Paleta primária: azul marinho (#1a365d) e coral (#ff6b6b)"
"Esquema dark mode com acentos em roxo neon"
"Monocromático com um único tom de destaque"
"Gradiente de sunrise: laranja → rosa → roxo"
"Cores da marca: [insira cores específicas]"
```

### 2.3 Tipografia

```
"Fonte sans-serif moderna (tipo Inter ou Roboto)"
"Fonte serif para títulos (tipo Playfair Display)"
"Fonte monospace para dados/código (tipo Fira Code)"
"Hierarquia clara: H1=48px bold, H2=32px medium, body=16px regular"
```

### 2.4 Layout & Espaçamento

```
"Grid de 12 colunas, max-width 1200px, padding generoso"
"Layout assimétrico, quebrando a grid em seções específicas"
"Mobile-first, responsivo até 320px"
"Sidebar fixa à esquerda, conteúdo scrollável"
"Card-based design com grid de 3 colunas no desktop"
```

---

## ⚙️ Camada 3 — Comportamento & Interatividade

### 3.1 Estados de Elementos

Sempre peça os estados:

```
"Botão com estados: default, hover, active, disabled, loading"
"Input com estados: vazio, preenchido, foco, erro, sucesso"
"Card com estados: default, hover (elevação + sombra), selecionado"
```

### 3.2 Animações & Transições

```
"Animação suave de fade-in ao scrollar (scroll-triggered)"
"Micro-interações nos botões: scale(1.02) no hover, ripple effect no click"
"Loading skeleton enquanto dados carregam"
"Transição de página suave (page transition)"
"Parallax sutil na hero section"
"Typing effect no headline principal"
```

### 3.3 Funcionalidades Específicas

```
"Menu hambúrguer com animação de morphing no mobile"
"Modal com backdrop blur e animação de slide-up"
"Tabs com indicador animado que se move entre as opções"
"Accordion com animação de expand/collapse suave"
"Carousel/Slider com swipe no mobile e navegação por dots"
"Toast notifications que entram pela direita e auto-dismiss em 5s"
"Search com autocomplete e highlight dos resultados"
"Drag and drop para reordenar itens de lista"
```

---

## 📱 Camada 4 — Responsividade & Acessibilidade

```
"Responsivo: mobile (320px), tablet (768px), desktop (1024px+), wide (1440px+)"
"Touch-friendly: botões mínimo 44x44px, espaçamento adequado para dedos"
"Acessível: contraste WCAG AA, navegação por teclado, labels para screen readers"
"Reduzir motion para quem tem preferência por menos animação"
```

---

## 🚫 Camada 5 — Restrições & O Que Evitar

```
"Não usar frameworks externos (React, Vue, Angular) — apenas HTML/CSS/JS vanilla"
"Não usar bibliotecas de CSS externas (Bootstrap, Tailwind) — CSS puro"
"Compatível apenas com Chrome/Edge últimas versões"
"Performance: primeiro paint em menos de 1s, nada de imagens pesadas"
"Sem dependências externas, tudo inline ou em arquivos separados"
"Evitar textos genéricos de placeholder (Lorem Ipsum), usar conteúdo realista"
```

---

## 🧩 Exemplos Completos de Prompts

### Exemplo 1 — Landing Page

```
Crie uma landing page para um app de meditação chamado "Mindful".

ESTRUTURA:
- Hero section com headline "Encontre sua calma", subheadline curta, CTA "Começar gratuitamente" e ilustração de uma pessoa meditando
- Seção de features com 3 cards: "Meditações guiadas", "Rastreamento de humor", "Sons relaxantes" — cada um com ícone e descrição curta
- Depoimentos em carrossel com 3 reviews de usuários
- Preços: plano Free e Pro lado a lado, com destaque no Pro
- Footer com links e newsletter signup

ESTILO:
- Paleta: verde sálvia (#84a98c), branco quebrado (#f8f9fa), cinza escuro (#212529)
- Tipografia: sans-serif arredondada e amigável (tipo Nunito)
- Estilo: organico, calmante, muito whitespace, bordas arredondadas
- Animações: elementos fade-in suave ao scrollar, cards elevam no hover

COMPORTAMENTO:
- Menu fixo no topo com blur no scroll
- Smooth scroll entre seções
- Mobile-first, totalmente responsivo
- Apenas HTML/CSS/JS vanilla, sem frameworks
```

### Exemplo 2 — Dashboard

```
Crie um dashboard de analytics para uma loja online.

ESTRUTURA:
- Sidebar fixa à esquerda com: Logo, Dashboard, Pedidos, Clientes, Produtos, Configurações
- Header com: título da página, search bar, notificações (badge com número), avatar do usuário
- Cards de métricas no topo: Receita total, Pedidos hoje, Ticket médio, Taxa de conversão — cada um com ícone e variação percentual (positivo/negativo)
- Gráfico de linha: "Vendas nos últimos 30 dias" com tooltip no hover
- Tabela: "Últimos pedidos" com colunas ID, Cliente, Data, Valor, Status (com badges coloridos)

ESTILO:
- Tema: light mode, clean e profissional
- Cores: branco, cinza claro de fundo, azul (#0d6efd) como primária
- Tipografia: Inter, tamanhos consistentes
- Cards com sombra sutil, bordas arredondadas

COMPORTAMENTO:
- Sidebar colapsa em ícones no tablet/mobile
- Gráfico interativo com hover states
- Tabela com paginação e ordenação por coluna
- Toast notification ao marcar pedido como entregue
- Loading state nos cards enquanto "carrega" dados

RESTRIÇÕES:
- Apenas HTML/CSS/JS vanilla
- Sem bibliotecas de gráficos externas (use SVG/Canvas simples)
- Dados mock realistas, não genéricos
```

### Exemplo 3 — Formulário Complexo

```
Crie um formulário de cadastro multi-step para um serviço de assinatura.

ESTRUTURA (3 passos):
Passo 1 — Dados pessoais: Nome completo, Email, Telefone (com máscara), CPF (com máscara e validação)
Passo 2 — Endereço: CEP (com busca automática), Rua, Número, Complemento, Bairro, Cidade, Estado
Passo 3 — Plano: Cards lado a lado — Básico (R$29), Pro (R$59, destaque), Enterprise (R$99) — cada um com lista de features e botão selecionar
- Barra de progresso no topo mostrando "Etapa X de 3"
- Botões: "Voltar" (quando aplicável), "Próximo" / "Finalizar cadastro"

ESTILO:
- Card centralizado, max-width 600px, sombra elegante
- Cores: fundo cinza claro, card branco, primária roxa (#6f42c1)
- Inputs com borda que muda de cor no foco
- Ícones de validação (check verde / X vermelho) nos campos

COMPORTAMENTO:
- Validação em tempo real (não espera clicar em próximo)
- Máscaras automáticas nos campos formatados
- Busca de CEP via API (simulada com dados mock)
- Navegação por steps com animação de slide
- Resumo dos dados no final antes de confirmar
- Estado de loading no botão de submit

RESTRIÇÕES:
- HTML/CSS/JS vanilla
- Validação completa em JavaScript
- Acessível (labels, aria-describedby para erros)
```

---

## 🗣️ Palavras-Chave por Categoria

### Tecnologia / Stack
```
HTML5 semântico, CSS3, JavaScript vanilla, ES6+
Single Page Application (SPA)
Progressive Web App (PWA)
Static site, Server-side rendering (SSR)
Component-based architecture
Web Components, Custom Elements
```

### Design Visual
```
Minimalista, clean, moderno, elegante, premium, futurista
Glassmorphism, Neumorphism, Skeuomorphism, Flat design
Material Design, Apple Human Interface, Fluent Design
Dark mode, Light mode, High contrast
Gradients, Mesh gradients, Aurora backgrounds
Micro-interactions, Hover effects, Focus states
```

### Layout
```
Grid system, Flexbox, CSS Grid
Responsive, Mobile-first, Desktop-first
Fluid layout, Fixed layout, Adaptive layout
Card-based, Magazine layout, Split-screen
Hero section, Above the fold, Below the fold
Sticky header, Fixed sidebar, Off-canvas menu
```

### Animação & Motion
```
Fade in, Slide up/down/left/right, Scale, Rotate
Parallax, Scroll-triggered animations
Page transitions, Loading states, Skeleton screens
Smooth scroll, Sticky elements on scroll
Spring physics, Easing functions (ease-in-out, cubic-bezier)
Reduced motion (prefers-reduced-motion)
```

### Componentes UI
```
Modal/Dialog, Drawer/Sidebar, Accordion, Tabs
Carousel/Slider, Masonry grid, Timeline
Breadcrumbs, Pagination, Stepper/Wizard
Toast/Snackbar, Tooltip, Popover, Dropdown
Data table com sorting, filtering, pagination
Search com autocomplete, Tags/Chips, Rating stars
```

### Acessibilidade (a11y)
```
WCAG 2.1 AA/AAA, Screen reader friendly
Keyboard navigation, Focus trapping, Skip links
ARIA labels, aria-expanded, aria-live
Color contrast ratio, Alt text for images
Semantic HTML: nav, main, section, article, aside
```

---

## 💡 Dicas Extras

1. **Sempre peça dados realistas** — "Use conteúdo realista, não Lorem Ipsum"
2. **Defina o nível de complexidade** — "Nível iniciante/intermediário/avançado"
3. **Peça comentários no código** — "Inclua comentários explicando decisões importantes"
4. **Solicite estrutura de arquivos** — "Organize em: index.html, css/styles.css, js/app.js"
5. **Peça explicações** — "Explique por que escolheu essa abordagem"
6. **Itere** — Primeiro peça o esqueleto, depois refinamentos
7. **Use referências visuais** — Links de sites reais, Dribbble, Behance
8. **Seja específico nas dimensões** — "Header com 64px de altura", "Cards com 320px de largura"

---

## 🔄 Template Rápido (Copie e Cole)

```
Crie um(a) [TIPO: landing page/dashboard/form/etc] para [OBJETIVO/PRODUTO].

ESTRUTURA:
- [Seção 1: descrição]
- [Seção 2: descrição]
- [Seção 3: descrição]

ESTILO:
- Paleta de cores: [cores]
- Tipografia: [fontes]
- Estilo geral: [mood/adjetivos]
- Referência visual: [site/designer/estilo]

COMPORTAMENTO:
- [Interação 1]
- [Interação 2]
- [Animação/estado 1]

RESTRIÇÕES:
- [Stack tecnológica]
- [O que evitar]
- [Requisitos especiais]
```

---

> 💾 Guarde este arquivo. Consulte sempre que for pedir algo. Com o tempo, você vai internalizar essa estrutura e seus prompts vão ficar cada vez mais precisos.
