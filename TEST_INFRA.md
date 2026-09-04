# Infraestrutura de Testes E2E (Dual Track) — Web Visual Auditor

**Projeto:** `projects/web_visual_auditor`  
**Autor:** Agente de Testes E2E (`teamwork_preview_test_writer_e2e`)  
**Data:** 2026-09-03  
**Status:** ATIVO / DUAL-TRACK READY  
**Versão:** 1.0.0  

---

## 1. Visão Geral & Filosofia de Verificação

A biblioteca `projects/web_visual_auditor` implementa capacidades críticas de inspeção visual, análise geométrica de DOM e higienização semântica de conteúdo web. A robustez desse sistema exige uma estratégia de testes baseada no princípio **Offline-by-Design**, garantindo que 100% da suíte execute de forma determinística, sem depender de conectividade externa, APIs de terceiros ou serviços instáveis.

### Pilares Fundamentais da Trilha E2E:
1. **Determinismo Absoluto:** Todo teste produz exatamente o mesmo resultado (saída numérica, máscara de divergência, árvore DOM e texto semântico), independentemente de hardware, sistema operacional ou número de execuções.
2. **Isolamento e Independência de Estado:** Cada caso de teste é auto-contido. Toda criação de arquivos temporários utiliza fixtures isoladas (`tmp_path` do pytest) e é limpa automaticamente.
3. **Dual Track Progressivo:** A suíte de testes é estruturada para validação progressiva, permitindo verificar as interfaces e fixtures imediatamente e conectar cada módulo de implementação conforme disponibilizado pelos marcos (M1 a M5).
4. **Verificação Matemática Rigorosa:** A auditoria visual e o cálculo diferencial pixel a pixel são validados contra provas matemáticas exatas de contagem de pixels e percentuais de divergência.

---

## 2. Metodologias Formais de Projeto de Testes

Para garantir cobertura exaustiva de código e comportamento, foram aplicadas quatro metodologias formais de teste de software:

### 2.1. Category-Partition Method (Ostrand & Balcer)
A decomposição funcional segmentou os cinco requisitos em categorias discretas de entrada e partições de equivalência:

| Componente | Parâmetro / Categoria | Partições Válidas | Partições Inválidas / Excepcionais |
|---|---|---|---|
| **R1. Semantic Cleaner** | `raw_html` | - HTML semântico limpo<br>- HTML ruidoso (scripts, styles, SVGs, nós noscript)<br>- HTML com formatação/espaçamento irregular | - String vazia `""`<br>- `None`<br>- Conteúdo sem tags HTML |
| **R2. DOM Inspector** | `url_or_html` | - URL `file://` local<br>- Data URL `data:text/html,...`<br>- Código HTML estático injetado | - URL malformada<br>- Página com timeout/delay excessivo<br>- Página em branco |
| **R2. DOM Inspector** | `visibility` | - Elemento visível (dimensões > 0, opacity 1, display block/flex)<br>- Elemento semi-transparente | - `display: none`<br>- `visibility: hidden`<br>- Dimensões `0x0` pixels |
| **R3. Visual Regression** | `delta_canal` ($\Delta C$) | - $\Delta C = 0$ (idêntico)<br>- $1 \le \Delta C \le 15$ (antialiasing tolerado)<br>- $\Delta C > 15$ (divergência real) | - Cores fora do espectro 0-255 |
| **R3. Visual Regression** | `image_dimensions` | - Dimensões idênticas (ex: 100x100 vs 100x100) | - Dimensões diferentes (100x100 vs 120x100) $\to$ `DimensionMismatchError` |
| **R4. Component Auditor** | `selector` | - Tag simples (`button`, `header`)<br>- ID (`#primary-action-btn`)<br>- Classe composta (`.btn.btn-primary`) | - Seletor inexistente no DOM (`#not-found`) $\to$ `ElementNotFoundError`<br>- Seletor com sintaxe CSS inválida |
| **R5. CLI / Suite** | `subcommands` | - `search`, `dom-inspect`, `visual-diff`, `component-diff`, `suite` | - Subcomando desconhecido<br>- Parâmetros obrigatórios ausentes |

---

### 2.2. Boundary Value Analysis (BVA)
O teste de limites foca nos valores limítrofes onde ocorrem as transições de comportamento:

1. **Limiar de Antialiasing de Canal de Cor:**
   - $\Delta C = 0$: Identidade exata ($\text{different\_pixels} = 0$, $\text{diff\_percentage} = 0.0\%$).
   - $\Delta C = 15$: Limite máximo da tolerância de ruído ($\text{different\_pixels} = 0$, $\text{diff\_percentage} = 0.0\%$).
   - $\Delta C = 16$: Primeiro valor de divergência perceptível ($\text{different\_pixels} \ge 1$, $\text{diff\_percentage} > 0.0\%$, pixel colorido em `#FF0000`).
   - $\Delta C = 255$: Divergência máxima possível (ex: branco puro `(255,255,255)` vs preto puro `(0,0,0)`).

2. **Razão Diferencial de Pixels:**
   - 0 pixels alterados em 10.000: Exatamente $0.00\%$.
   - 400 pixels alterados em 10.000: Exatamente $4.00\%$ ($20 \times 20$ pixels em canvas $100 \times 100$).
   - 10.000 pixels alterados em 10.000: Exatamente $100.00\%$.

3. **Geometria de Nós do DOM:**
   - Elemento visível padrão: $width = 120.0$, $height = 40.0$, $x \ge 0$, $y \ge 0$, `is_visible = True`.
   - Elemento colapsado: $width = 0.0$, $height = 0.0$, `is_visible = False`.
   - Elemento oculto via CSS: `display: none` $\to$ `is_visible = False`.

4. **Timeouts de Carregamento:**
   - Carregamento instantâneo via `data:` URL: $\le 100\text{ms}$.
   - Timeout nominal de 15.000ms com acionamento do fallback `wait_until="domcontentloaded"` para não travar o processo.

---

### 2.3. Pairwise Testing (Testes Combinatórios)
Para mitigar a explosão combinatória sem perder eficácia, pares de parâmetros ortogonais foram formalizados:

| Caso | Origem da Entrada | Tipo de Seletor | Estado do Componente | Resultado Esperado |
|---|---|---|---|---|
| P1 | Fixture estática (`file://`) | Tag semântica (`header`) | Visível, dimensões estáveis | Bounding box extraída com sucesso |
| P2 | Data URL (`data:text/html,...`) | Classe CSS (`.btn-primary`) | Visível, interativo | Captura de screenshot isolada |
| P3 | Fixture estática (`file://`) | ID (`#hidden-element`) | Oculto (`display: none`) | `is_visible == False` |
| P4 | Data URL (`data:text/html,...`) | Seletor inexistente (`#none`) | Não existe | `ElementNotFoundError` disparado |
| P5 | Imagem sintética PIL (RGB) | N/A | Divergência $\Delta C \le 15$ | 0% diff, sem máscara vermelha |
| P6 | Imagem sintética PIL (RGB) | N/A | Divergência $\Delta C > 15$ | Diff detectado, máscara com `#FF0000` |
| P7 | Imagem sintética PIL (Dimensões !=) | N/A | $100\times100$ vs $120\times100$ | `DimensionMismatchError` disparado |

---

### 2.4. Workload & Stress Modeling
A infraestrutura inclui cenários de alta densidade estrutural:
- **Fixtures com Alto Volume de Ruído:** `sample_noisy_article.html` contém scripts com injeções inline, trackers simulados, nós SVG com múltiplos caminhos vetoriais, blocos de estilo CSS de alta especificidade e nós de telemetria.
- **Resiliência a Timeout:** Validação da política de renderização do Playwright sob páginas com execução contínua de timers assíncronos.

---

## 3. Inventário Canônico dos 4 Tiers de Testes

A suíte E2E em `projects/web_visual_auditor/tests/test_e2e.py` organiza-se rigorosamente em 4 Tiers:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 4: Real-World Scenarios (End-to-End Scenarios)         │
│ - Auditoria editorial completa em artigo com ruído severo   │
│ - Regressão visual de componente sob layout responsivo      │
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Cross-Feature Integration Tests                     │
│ - Pipeline integrado DOM Inspector -> Captura -> Diff       │
│ - Extração semântica + inspeção geométrica encadeadas       │
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Boundary, Corner & Error Handling Tests             │
│ - BVA de canais de cor (15 vs 16)                           │
│ - Mismatch de dimensões (DimensionMismatchError)            │
│ - Tratamento de seletores inexistentes e nós ocultos        │
├─────────────────────────────────────────────────────────────┤
│ Tier 1: Core Feature Coverage (Happy Paths)                 │
│ - R1: Limpeza semântica com BeautifulSoup                   │
│ - R2: Inspeção de nós chave do DOM via Playwright           │
│ - R3: Comparação diferencial 0% PIL                         │
│ - R4: Isolamento e snapshot de micro-componentes            │
│ - R5: Execução orquestrada e subcomandos da CLI             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Fixtures Determinísticas & Geradores Sintéticos

### 4.1. Fixtures HTML Estáticas
Localizadas em `projects/web_visual_auditor/tests/fixtures/`:

1. **`sample_page.html`**:
   - Página limpa, semântica e com geometria previsível.
   - Contém: `<header id="main-header">`, `<nav id="navbar">`, `<h1 id="page-title">`, `<main id="main-content">`, `<article id="featured-article">`, `<button id="primary-action-btn">`, `<button id="secondary-btn">`, `<div id="hidden-element">`.
   - Dimensões e posicionamento fixados por CSS inline/estilo interno para conferir estabilidade milimétrica nas bounding boxes.

2. **`sample_noisy_article.html`**:
   - Página realista para testar o purificador semântico BeautifulSoup (R1).
   - Contém:
     - Tags `<script>` com código executável e dados de telemetria (`window.dataLayer`).
     - Tags `<style>` inline com seletores complexos.
     - Elementos `<svg>` com paths vetoriais densos.
     - Elementos `<noscript>` com avisos obsoletos.
     - Comentários HTML diversos (`<!-- Analytics tracking snippet -->`).
     - Conteúdo editorial nobre (títulos, parágrafos, blockquotes, listas) que deve ser preservado integralmente e sem contaminação.

### 4.2. Gerador Sintético de Imagens (`image_fixtures.py`)
Localizado em `projects/web_visual_auditor/tests/fixtures/image_fixtures.py`:

- **`generate_identical_pair(width=100, height=100, color=(255, 255, 255))`**:
  Gera duas imagens idênticas.
  *Garantia matemática:* $\Delta C = 0$, $0$ pixels divergentes, diff $= 0.0\%$.

- **`generate_subtle_noise_pair(width=100, height=100, base_color=(255, 255, 255), noise_delta=10)`**:
  Gera par com variação de cor onde $\Delta C \le 15$ (ex: branco 255 vs cinza claro 245, $\Delta C = 10 \le 15$).
  *Garantia matemática:* Todos os pixels dentro da tolerância de antialiasing $\to 0$ pixels divergentes, diff $= 0.0\%$.

- **`generate_divergent_square_pair(width=100, height=100, base_color=(255, 255, 255), square_color=(0, 0, 0), square_size=20, top_left=(40, 40))`**:
  Gera baseline branca e current com um quadrado preto de $20 \times 20$ pixels em `(40, 40, 59, 59)`.
  *Garantia matemática:*
  $$\text{Área do quadrado} = 20 \times 20 = 400\text{ pixels}$$
  $$\text{Área total} = 100 \times 100 = 10.000\text{ pixels}$$
  $$\text{Percentual exato de divergência} = \frac{400}{10.000} \times 100\% = 4.00\%$$
  $$\text{Diferença de canal} = |255 - 0| = 255 > 15 \implies \text{Divergência confirmada}$$

- **`generate_dimension_mismatch_pair(dim_a=(100, 100), dim_b=(120, 100))`**:
  Gera duas imagens com resoluções incompatíveis para verificação de exceção `DimensionMismatchError`.

---

## 5. Semântica de Execução & Comandos Oficiais

### 5.1. Execução via Pytest
A partir da raiz do repositório:
```powershell
uv run pytest projects/web_visual_auditor/tests -v --tb=short
```

Execução focada apenas na suíte E2E:
```powershell
uv run pytest projects/web_visual_auditor/tests/test_e2e.py -v
```

Execução por Tier específico:
```powershell
uv run pytest projects/web_visual_auditor/tests/test_e2e.py -k "TestTier1" -v
uv run pytest projects/web_visual_auditor/tests/test_e2e.py -k "TestTier2" -v
uv run pytest projects/web_visual_auditor/tests/test_e2e.py -k "TestTier3" -v
uv run pytest projects/web_visual_auditor/tests/test_e2e.py -k "TestTier4" -v
```

### 5.2. Validação de Estilo e Tipagem (Linter)
```powershell
uv run ruff check projects/web_visual_auditor
```

---

## 6. Governança e Regras de Manutenção

1. **Zero Modificações em Código de Implementação:** Test Writers e agentes de QA operam estritamente sobre arquivos de teste (`tests/`) e documentação de teste. Qualquer defeito no código de produção deve ser escalado.
2. **Determinismo em CI/CD:** Toda fixture em disco deve ser estática e imutável. Arquivos de saída de diff gerados durante os testes devem ser direcionados para diretórios temporários (`tmp_path`) para não poluir o repositório de código.
3. **Assertividade Precisa:** Comparações numéricas de ponto flutuante devem utilizar `pytest.approx` com tolerância estrita (`abs=1e-3`) ou igualdade exata para inteiros e razões comprovadas.
