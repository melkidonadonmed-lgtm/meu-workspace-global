# Rubrica de pontuação — Frontend Auditor

Cada item tem pontos fixos. Nota da dimensão = (pontos obtidos / pontos avaliáveis) × 100.
Itens marcados `[N/A]` saem do denominador. Meio ponto não existe: item vale 0, metade ou total, conforme critério de cada item.

## D1 — Funcionalidade (100 pts)

| # | Item | Pts | Critério |
|---|---|---|---|
| D1.1 | Renderização | 20 | Total: renderiza completo em ≤3s. Metade: renderiza com elementos faltando. Zero: tela branca/erro fatal |
| D1.2 | Console limpo | 10 | Total: 0 erros JS. Metade: só warnings. Zero: erros quebrando comportamento |
| D1.3 | Navegação e links | 12 | Total: todos os links/rotas funcionam, sem 404, sem dead ends. Metade: ≤2 quebrados |
| D1.4 | Controles interativos | 15 | Botões, toggles, menus, modais respondem com feedback visível. Testar os principais; total = todos respondem |
| D1.5 | Formulários e inputs | 12 | Validação presente, mensagens de erro claras, submit funciona. N/A se não há forms |
| D1.6 | Estados de interface | 12 | Loading, vazio e erro existem e são apresentáveis (não quebram layout). Metade se só parcialmente cobertos |
| D1.7 | Responsividade | 12 | Layout íntegro em 1440px e 390px, sem overflow horizontal, sem sobreposição. N/A se escopo é só desktop |
| D1.8 | Recursos externos | 7 | Fontes, imagens, ícones e scripts carregam sem 4xx/5xx |

## D2 — Design visual (100 pts)

| # | Item | Pts | Critério |
|---|---|---|---|
| D2.1 | Hierarquia visual | 18 | Um foco claro por tela; título > subtítulo > corpo distinguíveis à primeira vista; ação primária evidente |
| D2.2 | Consistência de tokens | 16 | Espaçamentos, raios de borda, sombras e pesos seguem um conjunto limitado e repetido (máx. ~4 valores de raio, escala de espaçamento regular) |
| D2.3 | Paleta | 16 | ≤5 cores de interface + semânticas; cor usada com intenção (estado/ação), não decoração aleatória; acento único identificável |
| D2.4 | Alinhamento e grid | 14 | Elementos alinham em eixos compartilhados; margens laterais consistentes; nada "quase alinhado" |
| D2.5 | Densidade e respiro | 12 | Informação agrupada por proximidade; sem paredes de texto nem espaço desperdiçado; painéis não aninhados além de 2 níveis |
| D2.6 | Estados visuais | 10 | Hover/focus/active/selected distinguíveis e consistentes entre componentes |
| D2.7 | Qualidade de ícones/imagens | 8 | Ícones no mesmo estilo e traço; imagens nítidas e relevantes; zero placeholders ou arte quebrada |
| D2.8 | Movimento | 6 | Transições curtas (≤300ms) e com propósito; nada que distraia da tarefa. N/A se interface estática por natureza |

## D3 — Tipografia & conteúdo (100 pts)

| # | Item | Pts | Critério |
|---|---|---|---|
| D3.1 | Famílias e escala | 20 | ≤2 famílias (+mono opcional); escala com 4–6 degraus perceptíveis; título claramente maior que corpo |
| D3.2 | Legibilidade | 22 | Corpo ≥13px; line-height 1.4–1.7 em texto corrido; medida ≤75 caracteres; pesos suficientes contra o fundo |
| D3.3 | Fontes carregadas | 12 | Webfont renderiza (sem fallback quebrando métricas), `font-display` adequado, glifos do idioma presentes (ex.: acentos PT-BR) |
| D3.4 | Truncamento e overflow | 16 | Textos longos truncam com elipse ou quebram sem estourar containers; nada cortado no meio da linha visível |
| D3.5 | Hierarquia textual | 14 | Headings em ordem lógica (h1→h2→h3), labels consistentes (mesmo padrão de capitalização) |
| D3.6 | Microcopy | 16 | Botões com verbos claros, mensagens de erro que dizem o que fazer, placeholders úteis, sem lorem ipsum |

## D4 — Acessibilidade & técnica (100 pts)

| # | Item | Pts | Critério |
|---|---|---|---|
| D4.1 | Contraste WCAG | 24 | Texto normal ≥4.5:1, grande ≥3:1, componentes de UI ≥3:1 contra o fundo. Metade: falha só em texto secundário pequeno. **Fonte primária: saída do axe_scan (regra color-contrast)** — cada grupo de ocorrências sérias = −6 |
| D4.2 | Foco e teclado | 18 | Foco visível em todos os interativos; ordem de tabulação sensata; Esc fecha modais. **Fonte primária: bloco keyboard do behavioral_probe** — foco invisível em >30% dos stops = zero |
| D4.3 | Semântica e ARIA | 16 | Landmarks (`header/main/nav`), botões são `<button>`, ícones interativos têm nome acessível |
| D4.4 | Imagens e mídia | 10 | `alt` útil em imagens de conteúdo, vazio em decorativas. N/A se não há imagens |
| D4.5 | Formulários acessíveis | 12 | Todo input tem `<label>` associado; erros anunciados. N/A se não há forms |
| D4.6 | Meta e documento | 8 | `<title>` descritivo, viewport correto, `lang` no `<html>`, favicon presente |
| D4.7 | Peso e performance básica | 12 | Recursos totais razoáveis (<3MB inicial para página comum); imagens dimensionadas; sem biblioteca carregada sem uso |
| D4.8 | Tema claro/escuro | 8 | Se a UI declara os dois temas: auditar contraste nos dois (axe em ambos). Falhas só em um tema → metade. N/A se há tema único declarado |
| D4.9 | Movimento respeitoso | 4 | Animações reduzem ou param sob `prefers-reduced-motion`. N/A se estático |
| D4.10 | Segurança básica de front | 6 | Links externos com `rel="noopener"`, sem conteúdo misto, forms com `autocomplete` apropriado, sem dados sensíveis hardcoded no HTML |

## D5 — Robustez contextual (opcional, +bônus informativo)

Não entra na nota; registrar como observações:
- **Zoom 200%**: overflow horizontal ou perda de conteúdo (behavioral_probe testa)
- **Offline/rede lenta**: a página falha com dignidade ou quebra sem aviso
- **i18n**: se a UI suporta múltiplos idiomas, textos longos (simular alemão/finnico) não estouram containers

## Penalidades duras (após somar)

| Condição | Efeito |
|---|---|
| Tela branca / erro fatal de JS | nota final ≤ 20 |
| Lorem ipsum ou placeholder de conteúdo visível | −10 |
| Overflow horizontal no desktop | −8 |
| Conteúdo misto http/https quebrando recursos | −5 |

## Conversão da nota geral

Nota geral = D1×0,35 + D2×0,30 + D3×0,15 + D4×0,20, depois das penalidades.

- ≥90 **Excelente** — pronto para produção
- 75–89 **Bom** — melhorias de polimento
- 60–74 **Aceitável** — problemas maiores a resolver
- 40–59 **Fraco** — retrabalho significativo
- <40 **Crítico** — recomeçar a tela
