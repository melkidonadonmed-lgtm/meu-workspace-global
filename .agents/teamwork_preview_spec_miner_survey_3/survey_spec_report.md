# Relatório Exaustivo de Mineração de Especificações & Estratégia de Testes Determinísticos
**Pacote Alvo:** `projects/web_visual_auditor`  
**Autor:** `teamwork_preview_spec_miner_survey_3` (Specification Miner)  
**Fonte Autoritativa:** `c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md`  
**Data:** 2026-09-03  
**Status:** Concluído / Pronto para Arquitetura e Implementação  

---

## 1. Visão Geral & Escopo do Sistema

O pacote `projects/web_visual_auditor` é uma biblioteca e ferramenta CLI autônoma em Python voltada à inspeção visual, semântica e geométrica de aplicações web e bibliotecas de componentes (Design Systems). O sistema combina:
1. Pesquisa web com higienização semântica de artigos via BeautifulSoup.
2. Renderização headless e inspeção de geometria computada do DOM via Playwright.
3. Auditoria visual pixel a pixel com tolerância a antialiasing via Pillow (PIL).
4. Captura e regressão visual isolada de micro-componentes de design systems.
5. Interface CLI unificada e suíte orquestradora (`WebVisualAuditorSuite`).

---

## 2. Features Discovered (Tabela Canônica)

| # | Categoria | Feature | Descrição | Entradas | Saídas | Comportamento de Erro | Descoberto Via |
|---|-----------|---------|-----------|----------|--------|------------------------|----------------|
| 1 | Pesquisa Semântica | `clean_html_content` | Remoção de tags desnecessárias (`<script>`, `<style>`, `<svg>`, nós de tracking) e normalização de texto. | String HTML bruta ou objeto Soup | String de texto limpa e normalizada ou árvore purificada | Retorna string vazia ou levanta `ValueError` se o conteúdo for `None` | R1 em ORIGINAL_REQUEST.md |
| 2 | Pesquisa Semântica | `search_and_extract` | Execução de busca estruturada web e extração de artigos consolidados. | `query: str`, `max_results: int = 5`, `offline_html: str | None = None` | `list[SourceReference]` contendo título, URL e snippet | Captura falhas de rede com fallback gracioso; levanta `SearchExtractionError` em falha irrecuperável | R1 em ORIGINAL_REQUEST.md |
| 3 | Inspeção DOM | `inspect_dom_geometry` | Renderização headless e extração de coordenadas e atributos de nós-chave. | `url: str`, `selectors: list[str] | None = None`, `viewport: dict = {"width": 1280, "height": 720}` | `list[ComputedElementGeometry]` com bounding boxes e visibilidade | Timeout de carregamento com fallback de `domcontentloaded` para parsing parcial; `DOMInspectionError` se a página falhar totalmente | R2 em ORIGINAL_REQUEST.md |
| 4 | Inspeção DOM | `extract_key_elements` | Filtro e sumarização especializada dos elementos estruturais (`header`, `main`, `article`, `button`, `nav`, `h1`). | Instância de página Playwright ou árvore DOM | `list[DOMNodeSummary]` com id, classes, tag e visibilidade | Retorna lista vazia se nenhum elemento chave for localizado no documento | R2 em ORIGINAL_REQUEST.md |
| 5 | Auditoria Visual | `compare_pixel_diff` | Comparação pixel a pixel entre imagem baseline e imagem current via PIL com limiar `channel > 15`. | `baseline_path: str | Path`, `current_path: str | Path`, `diff_output_path: str | Path = "diff_result.png"`, `threshold: int = 15` | `VisualDiffResult` (percentual exato, total de pixels, pixels divergentes, caminho do diff) | Dispara `DimensionMismatchError` se as resoluções diferirem (com opção de resize); `FileNotFoundError` se arquivo ausente | R3 em ORIGINAL_REQUEST.md |
| 6 | Auditoria Visual | `generate_diff_mask` | Geração de máscara visual com destaque em vermelho puro `#FF0000` para pixels divergentes. | Duas instâncias PIL Image compatíveis | Imagem PIL (RGB/RGBA) salva em disco destacando pixels alterados | Trata canais alfa inconsistentes convertendo ambos para RGB/RGBA idênticos | R3 em ORIGINAL_REQUEST.md |
| 7 | Micro-Componentes | `capture_component_snapshot` | Isolamento e captura de screenshot focada exclusivamente na bounding box de um seletor CSS específico. | `url: str`, `selector: str`, `output_path: str | Path` | `ComponentSnapshot` (seletor, dimensões, caminho da imagem gerada) | Levanta `ElementNotFoundError` se o seletor CSS não existir no DOM ou não estiver visível | R4 em ORIGINAL_REQUEST.md |
| 8 | Micro-Componentes | `audit_component_diff` | Comparação de micro-componente isolado entre baseline e current gerando `diff_<selector>.png`. | `baseline_url: str`, `current_url: str`, `selector: str`, `output_dir: Path` | `ComponentDiffReport` com status de conformidade e métricas | Falha sinalizada no relatório com status FAILED se o diff exceder tolerância | R4 em ORIGINAL_REQUEST.md |
| 9 | Orquestração & CLI | `WebVisualAuditorSuite` | Classe principal para orquestrar pipeline unificado de pesquisa, inspeção DOM, diff geral e de componentes. | Configuração da suíte (URLs, seletores, limiares, diretório de saída) | Relatório consolidado em JSON/Dicionário e artefatos de imagem | Tratamento integrado de exceções acumulando status de cada etapa | R5 em ORIGINAL_REQUEST.md |
| 10 | CLI | `cli_entrypoint` | Interface de linha de comando com subcomandos (`search`, `dom-inspect`, `visual-diff`, `component-diff`, `suite`). | Argumentos de linha de comando (`sys.argv`) | Códigos de saída (0 para sucesso, 1 para regressão visual detectada, 2 para erro de sintaxe/ambiente) | Exibe mensagem de ajuda com `--help`; mensagens de erro explicativas no stderr | R5 em ORIGINAL_REQUEST.md |

---

## 3. Edge Cases (Tabela Canônica)

| # | Feature | Entrada / Cenário | Comportamento Observado & Especificado |
|---|---------|-------------------|----------------------------------------|
| 1 | `compare_pixel_diff` | Imagens 100% idênticas (mesmo tamanho, mesmos pixels) | `different_pixels == 0`, `diff_percentage == 0.0%`, `has_diff == False`. O arquivo diff é gerado sem marcas vermelhas. |
| 2 | `compare_pixel_diff` | Variação tênue de antialiasing (diferença em qualquer canal `<= 15`) | `different_pixels == 0`, `diff_percentage == 0.0%`, `has_diff == False`. Não gera falso positivo para rendering de fontes. |
| 3 | `compare_pixel_diff` | Variação com diferença no canal `> 15` (ex: `#FFFFFF` para `#EEEEEE` -> `|255-238| = 17 > 15`) | Pixel marcado como divergente, colorido em `#FF0000` puro na máscara, contabilizado em `different_pixels`. |
| 4 | `compare_pixel_diff` | Imagens de dimensões divergentes (ex: baseline 100x100 vs current 120x100) | Lança `DimensionMismatchError` informando as resoluções divergentes, a menos que flag `--allow-crop` ou pad seja ativado. |
| 5 | `clean_html_content` | HTML com injeções maliciosas, `<script>alert('xss')</script>`, CSS inline gigante e nós `<svg>` inline com 500 paths | Tags `<script>`, `<style>`, `<svg>`, `<noscript>`, `<meta>` e comentários removidos sumariamente. Retorna apenas texto limpo. |
| 6 | `clean_html_content` | HTML com múltiplos espaços contínuos, tabulações e quebras de linha irregulares | Texto normalizado para espaços únicos, quebras de parágrafo limpas sem lixo tipográfico. |
| 7 | `inspect_dom_geometry` | Página com scripts assíncronos pesados que nunca atingem `networkidle` | Timeout seguro configurado; ativação do fallback de carregamento `wait_until="domcontentloaded"` permitindo inspeção sem travar o processo. |
| 8 | `inspect_dom_geometry` | Elemento presente no DOM mas oculto (`display: none`, `visibility: hidden` ou `opacity: 0`) | `is_visible == False`. Coordenadas geométricas reportadas como `0, 0, 0, 0` ou conforme retornado pelo `getBoundingClientRect`. |
| 9 | `capture_component_snapshot` | Seletor CSS fornecido que corresponde a zero elementos na página | Lança exceção tipada `ElementNotFoundError` especificando o seletor não encontrado; o teste valida essa mensagem. |
| 10 | `capture_component_snapshot` | Seletor com caracteres especiais em CSS (ex: `.btn-primary.size\:lg > span`) | Sanitização do nome do arquivo para `diff_btn-primary_size_lg_span.png` evitando caracteres ilegais no sistema de arquivos do Windows/Linux. |
| 11 | `audit_component_diff` | Componente idêntico mas posicionado em outro ponto da tela (ex: dentro de layout responsivo) | Por isolar a captura via `element.screenshot()`, a comparação foca apenas na textura interna do componente, ignorando deslocamento global. |
| 12 | Execução Offline | Execução dos testes sem conexão com a internet ativa | 100% dos testes passam usando fixtures HTML locais (`file://` ou `data:text/html,...`) e imagens sintéticas em memória geradas via PIL. |

---

## 4. Detalhamento Técnico Minucioso dos Requisitos (R1 a R5)

### R1. Pesquisa Web & Extração Semântica de Artigos
* **Objetivo:** Permitir busca por tópicos na web e higienização robusta do conteúdo HTML para indexação ou auditoria de texto.
* **Componentes de Limpeza Obrigatórios:**
  - Devem ser decompostos e purgados da árvore DOM:
    * `<script>` (código executável, telemetria)
    * `<style>` (regras CSS e layouts)
    * `<svg>` (nós vetoriais que inflam texto com coordenadas XML)
    * `<noscript>` (fallbacks não renderizados)
    * `<meta>`, `<link>`, `<head>` (metadados de cabeçalho)
    * Comentários HTML (`<!-- ... -->`)
* **Critérios de Normalização Semântica:**
  - Eliminar repetições excessivas de quebras de linha (`\n\n\n+` -> `\n\n`).
  - Normalizar espaços em branco contínuos (`[\t ]+` -> ` `).
  - Remoção de tags vazias remanescentes.
* **Saída Estruturada:**
  - Objeto `SourceReference`:
    * `title: str` (Título limpo da página ou artigo)
    * `url: str` (URL canônica da fonte)
    * `snippet: str` (Resumo semântico textual sem tags HTML)
    * `raw_text: str | None` (Texto completo purificado opcional)
* **Resiliência Offline:**
  - O método deve aceitar injeção direta de `html_content` para testes determinísticos sem realizar requisições HTTP reais.

---

### R2. Inspeção de Geometria Computada do DOM
* **Objetivo:** Inspecionar e documentar a posição, dimensão e hierarquia dos elementos fundamentais do layout renderizado no browser.
* **Motor:** Playwright em modo headless (`chromium.launch(headless=True)`).
* **Política de Carregamento & Timeouts:**
  - Utilizar primariamente `page.goto(url, wait_until="domcontentloaded", timeout=15000)`.
  - Mecanismo de fallback: se a página tiver requisições secundárias pendentes (ex: WebSockets, analytics), o auditor não deve abortar; após `domcontentloaded`, uma espera passiva curta (ex: 500ms) ou `wait_for_load_state("load", timeout=5000)` com captura graciosa de timeout garante o estado renderizável.
* **Elementos DOM Chave Obrigatórios:**
  O auditor deve inspecionar obrigatoriamente os seguintes seletores estruturais e semânticos:
  1. `header` (Cabeçalhos estruturais e topo de página)
  2. `main` (Conteúdo primário da página)
  3. `article` (Módulos de conteúdo autônomo e notícias)
  4. `button` (Componentes interativos de ação e formulário)
  5. `nav` (Barras de navegação e menus)
  6. `h1` (Títulos principais hierárquicos)
  *(Com suporte a seletores adicionais configuráveis: `footer`, `section`, `form`, etc.)*
* **Atributos Obrigatórios a Extrair para Cada Elemento:**
  1. `x: float` (Coordenada horizontal esquerda obtida via `getBoundingClientRect().left` ou `.x`)
  2. `y: float` (Coordenada vertical superior obtida via `getBoundingClientRect().top` ou `.y`)
  3. `width: float` (Largura física computada em pixels `getBoundingClientRect().width`)
  4. `height: float` (Altura física computada em pixels `getBoundingClientRect().height`)
  5. `id: str | None` (Identificador único do elemento no DOM)
  6. `classes: list[str]` (Lista de classes CSS computadas a partir do atributo `class`)
  7. `visibilidade: bool` (`is_visible`: determinado por `display !== 'none'`, `visibility !== 'hidden'`, `opacity > 0` e dimensões `width > 0 && height > 0`)
  8. `tag: str` (Nome canônico da tag HTML em minúsculas)
  9. `text_preview: str` (Prévia do texto interno até 100 caracteres)

---

### R3. Auditoria Visual e Regressão Diferencial Pixel a Pixel
* **Objetivo:** Detectar alterações visuais milimétricas entre duas capturas de tela (baseline vs current) com alta precisão e sem falsos positivos gerados por antialiasing.
* **Biblioteca:** Pillow (PIL) em Python puro.
* **Limites Numéricos e Regras Algorítmicas:**
  - **Tolerância a Antialiasing (Canal):**
    * Seja um pixel da imagem baseline com canais $(R_1, G_1, B_1)$ e o respectivo pixel da imagem current $(R_2, G_2, B_2)$.
    * A divergência de canal é avaliada por:
      $$\Delta C = \max(|R_1 - R_2|, |G_1 - G_2|, |B_1 - B_2|)$$
    * **Critério Estrito:** Um pixel é considerado **Divergente (Mismatch)** se e somente se:
      $$\Delta C > 15$$
    * Se $\Delta C \le 15$, a diferença é considerada ruído aceitável de sub-pixel/antialiasing e o pixel é tratado como idêntico ($\Delta C = 0$).
  - **Destaque Visual na Máscara:**
    * Pixels onde $\Delta C > 15$ recebem a cor **Vermelho Puro `#FF0000`** (RGB: `(255, 0, 0)` ou RGBA: `(255, 0, 0, 255)`).
    * Pixels onde $\Delta C \le 15$ são representados com a imagem de fundo esmaecida (ex: em escala de cinza atenuada com opacidade de 30% a 50%) para conferir contexto visual exato da localização da falha.
  - **Métricas Numéricas Computadas:**
    * `total_pixels: int = width * height`
    * `different_pixels: int` (Soma total dos pixels onde $\Delta C > 15$)
    * `diff_ratio: float = different_pixels / total_pixels`
    * `diff_percentage: float = (different_pixels / total_pixels) * 100.0`
    * `has_diff: bool = different_pixels > 0` (ou comparado a um `threshold_percentage: float = 0.0`)
  - **Artefato de Saída:**
    * Arquivo obrigatório: `diff_result.png` gerado no caminho de saída configurado.

---

### R4. Auditoria Granular por Micro-Componentes de Design System
* **Objetivo:** Isolar elementos pontuais (botões, cards, modais, headers) para que pequenas alterações estruturais no restante da página não invalidem a auditoria do componente em si.
* **Mecanismo de Captura:**
  - Utilizar o método `locator.screenshot()` ou `element_handle.screenshot()` do Playwright para obter o buffer de imagem delimitado estritamente pela bounding box do componente.
* **Nomenclatura Canônica de Arquivos:**
  - Para cada seletor CSS auditado, o diff gerado deve seguir o padrão:
    `diff_<sanitized_selector>.png`
    *(Exemplo: seletor `button.btn-primary` -> `diff_button_btn-primary.png`)*
* **Relatório Estruturado:**
  - `ComponentDiffReport` agregando:
    * `selector: str`
    * `baseline_dimensions: tuple[int, int]` (width, height)
    * `current_dimensions: tuple[int, int]`
    * `diff_percentage: float`
    * `passed: bool` (se `diff_percentage <= threshold`)
    * `diff_image_path: str`

---

### R5. Interface CLI e Módulo Integrado
* **Classe Principal:** `WebVisualAuditorSuite`
  - Responsável pela inicialização de contextos, carregamento de configurações e execução unificada ou desacoplada dos módulos.
* **Interface de Linha de Comando (`cli.py`):**
  - Subcomandos mapeados:
    1. `search`:
       - `--query` / `-q` (termo de busca)
       - `--max-results` / `-n` (número máximo de artigos)
       - `--output` / `-o` (arquivo de saída JSON)
    2. `dom-inspect`:
       - `--url` / `-u` (URL ou caminho de arquivo local `file://`)
       - `--selectors` / `-s` (lista de seletores adicionais)
       - `--output` / `-o` (saída JSON com a árvore geométrica)
    3. `visual-diff`:
       - `--baseline` / `-b` (caminho da imagem de referência)
       - `--current` / `-c` (caminho da imagem atual)
       - `--output-diff` / `-d` (caminho da imagem diff gerada, padrão `diff_result.png`)
       - `--threshold` / `-t` (tolerância de canal, padrão 15)
    4. `component-diff`:
       - `--url-baseline` (URL baseline)
       - `--url-current` (URL current)
       - `--selector` (seletor CSS do micro-componente)
       - `--output-dir` (diretório de saída para `diff_<selector>.png`)
    5. `suite`:
       - Execução do pipeline completo a partir de um arquivo de configuração YAML/JSON.

---

## 5. Especificação dos Modelos de Dados (Tipagem Estrita)

Os modelos devem ser implementados utilizando `dataclasses` (com `@dataclass(frozen=True)` ou slots para alta performance) ou `pydantic.BaseModel`:

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass
class SourceReference:
    """Referência bibliográfica extraída de pesquisa semântica."""
    title: str
    url: str
    snippet: str
    raw_text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ComputedElementGeometry:
    """Geometria computada e coordenadas absolutas de um elemento no viewport."""
    tag: str
    x: float
    y: float
    width: float
    height: float
    id: str | None = None
    classes: list[str] = field(default_factory=list)
    is_visible: bool = True
    selector: str | None = None
    text_preview: str = ""

@dataclass
class DOMNodeSummary:
    """Sumário estrutural de nós-chave da hierarquia do DOM."""
    tag: str
    id: str | None
    classes: list[str]
    is_visible: bool
    geometry: ComputedElementGeometry | None = None
    children_count: int = 0

@dataclass
class VisualDiffResult:
    """Resultado da comparação diferencial pixel a pixel."""
    baseline_path: Path
    current_path: Path
    diff_image_path: Path
    total_pixels: int
    different_pixels: int
    diff_ratio: float
    diff_percentage: float
    has_diff: bool
    threshold_used: int = 15

@dataclass
class ComponentSnapshot:
    """Instantâneo de captura de micro-componente de UI."""
    selector: str
    image_path: Path
    width: int
    height: int
    bounding_box: dict[str, float]
    timestamp: float

@dataclass
class ComponentDiffReport:
    """Relatório comparativo de regressão em micro-componente."""
    selector: str
    baseline_snapshot: ComponentSnapshot
    current_snapshot: ComponentSnapshot
    diff_result: VisualDiffResult
    status: str  # "MATCH", "REGRESSION", "DIMENSION_MISMATCH"
```

---

## 6. Estratégia de Testes Locais Determinísticos (Offline-by-Design)

### 6.1. Princípios da Estratégia Offline
1. **Isolamento Total da Rede Externa:** Nenhum teste na suíte padrão deve depender de requisições à internet aberta (DuckDuckGo, Google, CDNs externas).
2. **Determinismo Absoluto:** Todo teste deve fornecer o mesmo resultado em qualquer máquina, sistema operacional e execução repetida.
3. **Velocidade de Execução:** Utilização de data URLs (`data:text/html,...`) e fixtures locais reduz o overhead de rede para zero.

### 6.2. Catálogo de Fixtures HTML Locais
As fixtures devem residir em `tests/fixtures/` ou `projects/web_visual_auditor/tests/fixtures/`:

1. `fixtures/clean_article.html`:
   - Documento contendo `<header>`, `<nav>`, `<h1>Título Principal</h1>`, `<main>`, `<article>`, parágrafos semânticos e `<button class="btn-action">Clique Aqui</button>`.
   - Utilizado para testar extração de nós-chave e cálculo geométrico.

2. `fixtures/dirty_article.html`:
   - Documento com tags poluídas:
     ```html
     <html>
       <head>
         <script>console.log('tracking');</script>
         <style>body { color: red; }</style>
       </head>
       <body>
         <script>alert(1);</script>
         <svg><circle cx="50" cy="50" r="40"/></svg>
         <h1>Artigo Limpo</h1>
         <p>Conteúdo real que deve sobreviver.</p>
         <noscript>Lixo não executado</noscript>
       </body>
     </html>
     ```
   - Utilizado para validar o purificador semântico BeautifulSoup de R1.

3. `fixtures/component_variant.html`:
   - Mesma base de `clean_article.html`, porém com o botão `<button>` alterado com estilo inline `background-color: #00FF00; width: 180px;`.
   - Utilizado para testar auditoria de micro-componentes de R4.

### 6.3. Geração Sintética de Imagens com PIL para Testes de Regressão Visual
Para testar a auditoria diferencial de R3 sem carregar imagens estáticas binárias do disco, a suíte de testes deve utilizar funções construtoras determinísticas:

```python
from PIL import Image, ImageDraw

def create_solid_image(width: int, height: int, color: tuple[int, int, int]) -> Image.Image:
    """Gera uma imagem retangular de cor sólida."""
    return Image.new("RGB", (width, height), color)

def create_image_with_square(
    width: int,
    height: int,
    bg_color: tuple[int, int, int],
    square_box: tuple[int, int, int, int],
    square_color: tuple[int, int, int]
) -> Image.Image:
    """Gera uma imagem com um elemento geométrico controlado."""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle(square_box, fill=square_color)
    return img
```

#### Matriz de Casos de Teste Matemáticos com Imagens Sintéticas:

1. **Teste Diff 0% (Idênticas):**
   - Imagem A: 100x100 com cor `(50, 100, 150)`.
   - Imagem B: 100x100 com cor `(50, 100, 150)`.
   - **Expectativa:**
     * `total_pixels == 10000`
     * `different_pixels == 0`
     * `diff_percentage == 0.0`
     * `has_diff == False`

2. **Teste de Tolerância de Antialiasing ($\le 15$):**
   - Imagem A: 100x100 com cor `(100, 100, 100)`.
   - Imagem B: 100x100 com cor `(115, 90, 105)` (Diferença máxima em qualquer canal = 15).
   - **Expectativa:**
     * `different_pixels == 0`
     * `diff_percentage == 0.0`
     * `has_diff == False` (Tolerância age perfeitamente, sem ruído)

3. **Teste de Divergência Acima da Tolerância ($> 15$):**
   - Imagem A: 100x100 branca `(255, 255, 255)`.
   - Imagem B: 100x100 branca com quadrado central de 20x20 pixels na cor preta `(0, 0, 0)`:
     * Coordenadas: `(40, 40, 59, 59)` -> 20 x 20 = 400 pixels alterados.
     * Diferença de canal: $|255 - 0| = 255 > 15$.
   - **Expectativa:**
     * `total_pixels == 10000`
     * `different_pixels == 400`
     * `diff_percentage == 4.0` (exatamente 4,00%)
     * `has_diff == True`
     * Verificação na máscara gerada `diff_result.png`: exatamente os 400 pixels na região `(40, 40)` a `(59, 59)` devem conter a cor `(255, 0, 0)` (#FF0000).

4. **Teste de Dimensões Divergentes:**
   - Imagem A: 100x100.
   - Imagem B: 120x100.
   - **Expectativa:** Lança `DimensionMismatchError`.

---

## 7. Matriz de Cobertura de Testes Pytest

| Arquivo de Teste | Função de Teste | Alvo / Requisito | Fixture / Entrada | Critério de Aprovação (Assert) |
|---|---|---|---|---|
| `test_researcher.py` | `test_clean_html_removes_scripts_and_styles` | R1 (BS4 cleaner) | `dirty_article.html` | Ausência de tags `script`, `style`, `svg`; texto útil preservado. |
| `test_researcher.py` | `test_clean_html_whitespace_normalization` | R1 (Normalização) | HTML com tabs e quebras `\n\n\n` | Espaços e quebras colapsados para formato padrão legível. |
| `test_researcher.py` | `test_search_offline_mode` | R1 (SourceReference) | Conteúdo HTML injetado | Retorna lista de `SourceReference` válidos sem tocar a rede. |
| `test_dom_auditor.py` | `test_extract_key_elements_geometry` | R2 (Playwright) | `clean_article.html` via `file://` ou data URL | Nós `header`, `main`, `article`, `button`, `nav`, `h1` presentes com coordenadas `x, y, w, h > 0`. |
| `test_dom_auditor.py` | `test_hidden_element_visibility` | R2 (Visibilidade) | HTML com elemento `display:none` | `is_visible == False` para o nó oculto. |
| `test_dom_auditor.py` | `test_page_load_timeout_fallback` | R2 (Timeout) | Página com sleep/delay sintético | Conclui via `domcontentloaded` sem lançar timeout não tratado. |
| `test_visual_regression.py` | `test_pixel_diff_identical_images` | R3 (PIL 0% diff) | Imagens sintéticas idênticas | `diff_percentage == 0.0`, `has_diff == False`. |
| `test_visual_regression.py` | `test_pixel_diff_within_tolerance_15` | R3 (Tolerância canal <= 15) | Imagem com canal divergente em 15 | `diff_percentage == 0.0`, `different_pixels == 0`. |
| `test_visual_regression.py` | `test_pixel_diff_above_tolerance_generates_mask` | R3 (Máscara #FF0000) | Imagem com quadrado preto 20x20 | `diff_percentage == 4.0`, máscara contém `(255, 0, 0)` na área modificada. Arquivo `diff_result.png` existe. |
| `test_visual_regression.py` | `test_dimension_mismatch_raises_error` | R3 (Dimensões) | Imagens 100x100 vs 120x100 | Lança `DimensionMismatchError`. |
| `test_component_auditor.py` | `test_capture_component_snapshot` | R4 (Playwright screenshot) | `clean_article.html` + seletor `button` | Gera arquivo de imagem contendo apenas o botão; dimensões conferem com bounding box. |
| `test_component_auditor.py` | `test_component_diff_generates_named_diff` | R4 (diff_<selector>.png) | Componente modificado vs baseline | Gera `diff_button.png`, detecta discrepância visual localizada. |
| `test_component_auditor.py` | `test_missing_selector_raises_error` | R4 (Seletor inexistente) | Seletor `#inexistente` | Lança `ElementNotFoundError`. |
| `test_cli.py` | `test_cli_search_subcommand` | R5 (CLI Search) | `--query "teste" --offline` | Exit code 0, saída formatada. |
| `test_cli.py` | `test_cli_visual_diff_subcommand` | R5 (CLI Diff) | `--baseline A.png --current B.png` | Exit code 1 quando há regressão, 0 quando idênticas. |
| `test_suite.py` | `test_web_visual_auditor_suite_full_pipeline` | R5 (Orquestrador) | Configuração completa da suíte | Execução integrada sem erros com relatório consolidado. |

---

## 8. Governança, Linter e Qualidade

1. **Conformidade de Linter:**
   - Todo o código desenvolvido deve passar no comando:
     ```powershell
     uv run ruff check .
     ```
   - Regras críticas:
     * Sem imports não utilizados.
     * Linhas limitadas a 100 caracteres.
     * Nenhuma cláusula desprotegida `except Exception` sem tratamento ou `# noqa: BLE001` com justificativa explícita.
2. **Tipagem e Anotações:**
   - Tipagem moderna Python 3.11+ (`list[str]`, `dict[str, Any]`, `X | None`).
   - Todos os métodos públicos e modelos de dados com type hints completos.
3. **Compatibilidade de Plataforma:**
   - Tratamento de caminhos através de `pathlib.Path` para compatibilidade total entre Windows (`\`) e Linux (`/`).
   - Normalização de URLs locais no formato `file:///C:/...` no Windows.

---
*Relatório de mineração de especificação finalizado e pronto para guiar o arquiteto e o implementador.*
