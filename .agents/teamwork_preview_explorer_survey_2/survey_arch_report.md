# Relatório de Arquitetura Técnica & Contratos de Interfaces
**Pacote**: `projects/web_visual_auditor`  
**Autor**: `teamwork_preview_explorer_survey_2` (Technical Architect & Survey Lead)  
**Data**: 2026-09-03  
**Status**: Concluído  

---

## 1. Sumário Executivo

Este documento estabelece o projeto técnico, arquitetura modular limpa, modelos de dados tipados e contratos de interface para o pacote autônomo `projects/web_visual_auditor`. O objetivo primário é fornecer um ecossistema modular e desacoplado para:
1. Pesquisa web com higienização e extração semântica de conteúdo (HTML limpo de scripts, styles e SVG);
2. Inspeção headless do DOM com Playwright, computando geometrias precisas (`getBoundingClientRect`) e hierarquias;
3. Regressão visual diferencial pixel a pixel via Pillow com tolerância a antialiasing (`channel > 15`) e geração de máscaras de calor em `#FF0000`;
4. Auditoria granular de micro-componentes de design systems delimitados por seletores CSS;
5. Suíte orquestradora e CLI com múltiplos subcomandos, garantindo 100% de execução determinística e testes locais sem dependência de internet.

---

## 2. Análise dos Requisitos Técnicos (R1 a R5)

### R1. Pesquisa Web & Extração Semântica de Artigos
- **Desafios e Solução**: A busca na web (DuckDuckGo / APIs públicas) deve ser tolerante a falhas de rede. O processamento de HTML com BeautifulSoup (`bs4`) deve remover cirurgicamente tags que distorcem o conteúdo textual ou trazem ruído de execução: `<script>`, `<style>`, `<svg>`, `<noscript>`, `<template>`, `<iframe />`, links e comentários.
- **Normalização**: Decodificação de entidades HTML (`&nbsp;`, `&amp;`), remoção de espaços em branco contíguos e consolidação de títulos, URLs e snippets em instâncias imutáveis de `SourceReference`.
- **Modo Offline Determinístico**: O motor deve permitir a injeção direta de strings HTML ou paths locais `file://`, permitindo que testes unitários e de integração validem a extração sem tráfego HTTP externo.

### R2. Inspeção de Geometria Computada do DOM
- **Desafios e Solução**: Uso do Playwright em modo headless para renderizar páginas dinâmicas. O tempo de carregamento deve respeitar `wait_until="domcontentloaded"` como estratégia padrão, possuindo mecanismo de fallback para `networkidle` ou timeout curto para evitar travamento em sites lentos ou com WebSockets abertos.
- **Extração Geométrica**: Execução de JavaScript no contexto da página (`page.evaluate`) para interrogar `getBoundingClientRect()` dos elementos-chave (`header`, `main`, `article`, `button`, `nav`, `h1`, `h2`, `section`, `footer`).
- **Atributos Capturados**: `x`, `y`, `width`, `height`, `id`, lista de `class_names`, `is_visible` (avaliado via dimensões > 0 e `style.display !== 'none'` e `style.visibility !== 'hidden'`), e texto resumido.
- **Modelos Associados**: `ComputedElementGeometry` e `DOMNodeSummary`.

### R3. Auditoria Visual e Regressão Diferencial Pixel a Pixel
- **Desafios e Solução**: Comparação puramente matemática e visual entre imagens (baseline vs current) utilizando Pillow (`PIL.Image`).
- **Métrica de Antialiasing**: Para cada pixel `(x, y)` em RGB/RGBA, calcula-se a diferença absoluta de cada canal:
  $$\Delta R = |R_{\text{base}} - R_{\text{curr}}|, \quad \Delta G = |G_{\text{base}} - G_{\text{curr}}|, \quad \Delta B = |B_{\text{base}} - B_{\text{curr}}|$$
  O pixel é classificado como divergente se e somente se:
  $$\max(\Delta R, \Delta G, \Delta B) > 15$$
- **Cálculo Percentual**:
  $$\text{diff\_percentage} = \left( \frac{\text{diff\_pixels\_count}}{\text{total\_pixels}} \right) \times 100.0$$
  Se as imagens forem idênticas, o resultado deve ser rigorosamente `0.0%` e `diff_pixels_count == 0`.
- **Geração da Máscara**: Produção de imagem PNG (`diff_result.png`) destacando pixels divergentes em vermelho puro `#FF0000` (RGBA `(255, 0, 0, 255)`), mantendo pixels concordantes com atenuação de contraste ou fundo semitransparente para permitir inspeção humana direta.
- **Incompatibilidade de Dimensões**: Se baseline e current tiverem dimensões distintas, o motor expande para um canvas unificado do tamanho máximo, contabilizando as áreas ausentes como divergência e sinalizando `dimensions_match=False`.

### R4. Auditoria Granular por Micro-Componentes de Design System
- **Desafios e Solução**: Permitir a auditoria focada em componentes isolados (botões, modais, cards de preço, navbars) sem a contaminação de alterações no restante da página.
- **Mecanismo**: Através de seletores CSS (ex: `button.btn-primary`, `nav.site-header`), o Playwright localiza o elemento via locator, obtém suas coordenadas e executa `locator.screenshot(path=...)`.
- **Comparação Diferencial**: O par de snapshots do componente é submetido ao `VisualRegressionEngine`, gerando `ComponentDiffReport` com imagem `diff_<selector_sanitized>.png`.
- **Tratamento de Ausência**: Caso o seletor não exista na baseline ou na versão atual, o sistema reporta o status `missing_in_baseline` ou `missing_in_current` sem lançar falha não tratada.

### R5. Interface CLI e Módulo Integrado
- **Desafios e Solução**: CLI intuitivo e unificado (`cli.py`), suportando subcomandos individuais e a execução da suíte completa.
- **Subcomandos**:
  - `search`: Consulta web e extração semântica com saída JSON ou Markdown;
  - `dom-inspect`: Inspeção estrutural e geométrica de nós-chave;
  - `visual-diff`: Comparação pixel a pixel de duas imagens existentes no disco;
  - `component-diff`: Inspeção e diff de seletores específicos entre duas URLs;
  - `suite`: Execução completa (DOM + Visual + Componentes) gerando relatório agregado e artefatos de auditoria.
- **Classe `WebVisualAuditorSuite`**: API em nível de código para automação e integração contínua.

---

## 3. Modelos de Dados Tipados (Pydantic v2)

Os modelos devem residir em `projects/web_visual_auditor/web_visual_auditor/models.py`. Utilizam `pydantic.BaseModel` com validação estrita, tipagem moderna Python 3.11+ e suporte nativo a serialização JSON.

```python
"""
projects/web_visual_auditor/web_visual_auditor/models.py
Modelos de dados canônicos para auditoria web e visual.
"""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class SourceReference(BaseModel):
    """Representa uma referência de fonte web higienizada."""
    model_config = ConfigDict(frozen=True)

    title: str = Field(description="Título normalizado do artigo ou página")
    url: str = Field(description="URL canônica da fonte")
    snippet: str = Field(description="Resumo ou trecho semântico inicial")
    cleaned_text: str = Field(description="Conteúdo textual higienizado sem tags ruidosas")
    raw_content: str | None = Field(default=None, description="HTML bruto original antes da limpeza")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais extraídos")
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp UTC da extração"
    )


class ComputedElementGeometry(BaseModel):
    """Coordenadas geométricas precisas do elemento computadas pelo viewport."""
    model_config = ConfigDict(frozen=True)

    x: float = Field(description="Coordenada X (left) em pixels")
    y: float = Field(description="Coordenada Y (top) em pixels")
    width: float = Field(description="Largura renderizada em pixels")
    height: float = Field(description="Altura renderizada em pixels")

    @property
    def area(self) -> float:
        """Calcula a área do elemento em pixels quadrados."""
        return max(0.0, self.width) * max(0.0, self.height)

    def intersects(self, other: "ComputedElementGeometry") -> bool:
        """Verifica se há sobreposição geométrica com outro elemento."""
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.height <= other.y
            or other.y + other.height <= self.y
        )


class DOMNodeSummary(BaseModel):
    """Resumo de inspeção hierárquica e visual de um nó do DOM."""
    tag_name: str = Field(description="Nome da tag HTML em lowercase (ex: button, header)")
    element_id: str | None = Field(default=None, description="Atributo id do nó, se presente")
    class_names: list[str] = Field(default_factory=list, description="Lista de classes CSS do nó")
    is_visible: bool = Field(description="Verdadeiro se o nó está renderizado e visível ao usuário")
    geometry: ComputedElementGeometry = Field(description="Geometria computada do nó")
    text_content: str | None = Field(default=None, description="Texto interno limpo do elemento")
    selector: str | None = Field(default=None, description="Seletor CSS sugerido para localização unívoca")
    attributes: dict[str, str] = Field(default_factory=dict, description="Atributos chave do elemento")


class VisualDiffResult(BaseModel):
    """Resultado da comparação pixel a pixel entre duas imagens."""
    baseline_path: str = Field(description="Caminho do arquivo de imagem base")
    current_path: str = Field(description="Caminho do arquivo de imagem atual sob auditoria")
    diff_image_path: str | None = Field(default=None, description="Caminho da máscara diferencial gerada")
    diff_pixels_count: int = Field(ge=0, description="Quantidade total de pixels divergentes")
    total_pixels_count: int = Field(ge=1, description="Quantidade total de pixels inspecionados")
    diff_percentage: float = Field(ge=0.0, le=100.0, description="Percentual exato de divergência (0.0 a 100.0)")
    channel_tolerance: int = Field(default=15, description="Limiar de tolerância por canal RGB")
    has_divergence: bool = Field(description="Verdadeiro se houver divergência além da tolerância")
    dimensions_match: bool = Field(default=True, description="Verdadeiro se ambas imagens possuíam o mesmo tamanho")
    baseline_dimensions: tuple[int, int] = Field(description="Dimensões (width, height) da imagem base")
    current_dimensions: tuple[int, int] = Field(description="Dimensões (width, height) da imagem atual")


class ComponentSnapshot(BaseModel):
    """Captura isolada de um micro-componente de interface."""
    selector: str = Field(description="Seletor CSS utilizado para isolar o componente")
    screenshot_path: str = Field(description="Caminho do arquivo de screenshot recortado")
    geometry: ComputedElementGeometry = Field(description="Geometria computada do componente na página")
    is_visible: bool = Field(description="Visibilidade do componente")
    tag_name: str | None = Field(default=None, description="Tag HTML do componente")
    inner_text: str | None = Field(default=None, description="Texto resumido contido no componente")
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp UTC da captura"
    )


class ComponentDiffReport(BaseModel):
    """Relatório comparativo de um micro-componente de design system."""
    selector: str = Field(description="Seletor CSS auditado")
    baseline_snapshot: ComponentSnapshot | None = Field(default=None, description="Snapshot base do componente")
    current_snapshot: ComponentSnapshot | None = Field(default=None, description="Snapshot atual do componente")
    diff_result: VisualDiffResult | None = Field(default=None, description="Resultado da regressão visual isolada")
    status: str = Field(description="Status da comparação: 'matched', 'diverged', 'missing_in_baseline', 'missing_in_current'")
    geometry_changed: bool = Field(default=False, description="Sinaliza se houve alteração posicional ou dimensional")


class SuiteAuditReport(BaseModel):
    """Relatório integrado consolidado de auditoria completa da aplicação."""
    baseline_url: str = Field(description="URL da baseline auditada")
    current_url: str = Field(description="URL atual auditada")
    execution_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp UTC da execução"
    )
    dom_nodes_baseline: list[DOMNodeSummary] = Field(default_factory=list)
    dom_nodes_current: list[DOMNodeSummary] = Field(default_factory=list)
    fullpage_diff: VisualDiffResult | None = Field(default=None)
    component_diffs: list[ComponentDiffReport] = Field(default_factory=list)
    overall_status: str = Field(description="'PASS' se não houver divergências críticas, senão 'FAIL'")
    summary_metrics: dict[str, Any] = Field(default_factory=dict)
```

---

## 4. Contratos de Interfaces por Módulo

### 4.1 Hierarquia de Exceções (`exceptions.py`)
```python
class WebVisualAuditorError(Exception):
    """Exceção base do pacote web_visual_auditor."""

class ResearchError(WebVisualAuditorError):
    """Erros relacionados a pesquisa web e busca."""

class SemanticExtractionError(ResearchError):
    """Falha na extração semântica ou parsing de HTML."""

class DOMAuditError(WebVisualAuditorError):
    """Erros durante inspeção de DOM via Playwright."""

class PageNavigationTimeoutError(DOMAuditError):
    """Timeout ao carregar página ou recurso web."""

class ElementNotFoundError(DOMAuditError):
    """Elemento ou seletor CSS obrigatório não encontrado no DOM."""

class VisualRegressionError(WebVisualAuditorError):
    """Erros na comparação visual de imagens."""

class ImageLoadError(VisualRegressionError):
    """Falha ao carregar ou decodificar arquivo de imagem."""

class ComponentAuditError(WebVisualAuditorError):
    """Falha ao isolar ou capturar screenshot de micro-componente."""
```

### 4.2 Módulo `researcher.py`
```python
class SemanticHTMLCleaner:
    REMOVE_TAGS: set[str] = {
        "script", "style", "svg", "noscript", "iframe",
        "template", "link", "meta", "object", "embed"
    }

    @classmethod
    def clean_html(cls, raw_html: str) -> str:
        """
        Higieniza o HTML removendo tags indesejadas, scripts, estilos e comentários.
        Retorna string de texto normalizado com espaços condensados.
        """

    @classmethod
    def extract_title_and_snippet(cls, raw_html: str) -> tuple[str, str]:
        """Extrai o título (<title> ou <h1>) e os primeiros parágrafos informativos."""


class WebResearcher:
    def __init__(self, http_client: Any | None = None, default_timeout_s: float = 15.0) -> None:
        """Inicializa o pesquisador permitindo injeção de cliente HTTP para testes."""

    def search(self, query: str, max_results: int = 5) -> list[SourceReference]:
        """
        Executa busca web estruturada.
        Em ambiente offline ou com fixtures, suporta mock determinístico.
        """

    def fetch_and_clean(self, url: str) -> SourceReference:
        """Faz o download da página via HTTP(S) ou file:// e higieniza com BeautifulSoup."""

    def clean_raw_html(self, raw_html: str, url: str = "file://local", title: str | None = None) -> SourceReference:
        """Higieniza diretamente uma string HTML, ideal para testes locais."""
```

### 4.3 Módulo `dom_auditor.py`
```python
class DOMAuditor:
    DEFAULT_KEY_TAGS: list[str] = [
        "header", "main", "article", "button", "nav",
        "h1", "h2", "h3", "section", "footer", "a"
    ]

    def __init__(self, headless: bool = True, default_timeout_ms: int = 15000) -> None:
        """Configura a instância headless do auditor Playwright."""

    async def inspect_url_async(
        self,
        url_or_path: str,
        key_tags: list[str] | None = None,
        viewport_size: dict[str, int] | None = None
    ) -> list[DOMNodeSummary]:
        """
        Navega até a URL (suporta http, https, file:// e data:) com wait_until='domcontentloaded'.
        Aplica fallback com pequeno delay se necessário para garantir hidratação.
        Executa JavaScript para extrair getBoundingClientRect de cada nó correspondente.
        """

    def inspect_url(
        self,
        url_or_path: str,
        key_tags: list[str] | None = None,
        viewport_size: dict[str, int] | None = None
    ) -> list[DOMNodeSummary]:
        """Wrapper síncrono para inspect_url_async."""

    async def capture_fullpage_screenshot_async(
        self,
        url_or_path: str,
        output_path: str | Path,
        viewport_size: dict[str, int] | None = None
    ) -> str:
        """Gera screenshot da página completa em modo headless e retorna o caminho absoluto."""

    def capture_fullpage_screenshot(
        self,
        url_or_path: str,
        output_path: str | Path,
        viewport_size: dict[str, int] | None = None
    ) -> str:
        """Wrapper síncrono de screenshot fullpage."""
```

### 4.4 Módulo `visual_regression.py`
```python
class VisualRegressionEngine:
    def __init__(self, channel_tolerance: int = 15) -> None:
        """Inicializa o motor com limiar de tolerância para ruído/antialiasing."""

    def compare_images(
        self,
        baseline_path: str | Path,
        current_path: str | Path,
        diff_output_path: str | Path | None = None
    ) -> VisualDiffResult:
        """
        Carrega duas imagens via Pillow, valida dimensões, compara pixel a pixel,
        destaca diferenças em vermelho puro #FF0000 e salva a máscara se solicitado.
        """

    def compare_pixels(
        self,
        img_baseline: Image.Image,
        img_current: Image.Image,
        diff_output_path: str | Path | None = None
    ) -> VisualDiffResult:
        """Núcleo computacional puro recebendo instâncias de PIL.Image."""
```

### 4.5 Módulo `component_auditor.py`
```python
class ComponentAuditor:
    def __init__(
        self,
        visual_engine: VisualRegressionEngine | None = None,
        dom_auditor: DOMAuditor | None = None
    ) -> None:
        """Inicializa o auditor de componentes injetando dependências visuais e de DOM."""

    async def capture_component_snapshot_async(
        self,
        url_or_path: str,
        selector: str,
        output_path: str | Path
    ) -> ComponentSnapshot:
        """Isola o elemento pelo seletor CSS e executa element.screenshot()."""

    def capture_component_snapshot(
        self,
        url_or_path: str,
        selector: str,
        output_path: str | Path
    ) -> ComponentSnapshot:
        """Wrapper síncrono para captura de componente."""

    def compare_component_snapshots(
        self,
        baseline_snapshot: ComponentSnapshot,
        current_snapshot: ComponentSnapshot,
        diff_output_path: str | Path | None = None
    ) -> ComponentDiffReport:
        """Executa diff visual exclusivo sobre os dois snapshots isolados do componente."""

    async def audit_components_async(
        self,
        baseline_url: str,
        current_url: str,
        selectors: list[str],
        output_dir: str | Path
    ) -> list[ComponentDiffReport]:
        """Audita múltiplos micro-componentes de design system entre duas versões da página."""

    def audit_components(
        self,
        baseline_url: str,
        current_url: str,
        selectors: list[str],
        output_dir: str | Path
    ) -> list[ComponentDiffReport]:
        """Wrapper síncrono para audit_components_async."""
```

### 4.6 Módulo `suite.py` & `cli.py`
```python
class WebVisualAuditorSuite:
    def __init__(
        self,
        researcher: WebResearcher | None = None,
        dom_auditor: DOMAuditor | None = None,
        visual_engine: VisualRegressionEngine | None = None,
        component_auditor: ComponentAuditor | None = None
    ) -> None:
        """Instancia e orquestra os quatro subsistemas principais."""

    def run_full_audit(
        self,
        baseline_url: str,
        current_url: str,
        component_selectors: list[str] | None = None,
        output_dir: str | Path = "audit_reports"
    ) -> SuiteAuditReport:
        """
        Executa o pipeline completo:
        1. Inspeção de DOM baseline e current;
        2. Screenshot e diff visual fullpage (gerando diff_result.png);
        3. Snapshots e diffs granulares para cada seletor de componente;
        4. Geração de relatório consolidado (JSON e Markdown).
        """
```

---

## 5. Estratégia de Empacotamento e CLI

### 5.1 Estrutura de Diretórios Recomendada
```
projects/web_visual_auditor/
├── pyproject.toml
├── README.md
├── web_visual_auditor/
│   ├── __init__.py
│   ├── models.py
│   ├── exceptions.py
│   ├── researcher.py
│   ├── dom_auditor.py
│   ├── visual_regression.py
│   ├── component_auditor.py
│   ├── suite.py
│   └── cli.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── fixtures/
    │   ├── sample_article.html
    │   ├── sample_design_system.html
    │   ├── sample_design_system_v2.html
    │   ├── baseline_button.png
    │   └── modified_button.png
    ├── test_researcher.py
    ├── test_dom_auditor.py
    ├── test_visual_regression.py
    ├── test_component_auditor.py
    ├── test_suite.py
    └── test_cli.py
```

### 5.2 Especificação do `pyproject.toml`
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "web-visual-auditor"
version = "0.1.0"
description = "Auditoria visual, regressão pixel a pixel e inspeção geométrica do DOM com agentes modulares"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    { name = "Equipe de Arquitetura de IA", email = "ai-arch@empresa.com" }
]
dependencies = [
    "pydantic>=2.8.0",
    "pillow>=10.0.0",
    "beautifulsoup4>=4.12.0",
    "playwright>=1.40.0",
    "httpx>=0.27.0",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.6.0",
]

[project.scripts]
web-visual-auditor = "web_visual_auditor.cli:main"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["."]
```

### 5.3 CLI Subcommands
O entrypoint `cli.py` utilizará `argparse` nativo do Python (evitando dependências externas não estritamente necessárias e garantindo 100% de compatibilidade):
1. `search`:
   - `web-visual-auditor search --query "design tokens" --max-results 5 [--output json]`
2. `dom-inspect`:
   - `web-visual-auditor dom-inspect --url "file:///path/to/page.html" [--tags header,nav,button] [--output json]`
3. `visual-diff`:
   - `web-visual-auditor visual-diff --baseline baseline.png --current current.png [--output-diff diff_result.png] [--tolerance 15]`
4. `component-diff`:
   - `web-visual-auditor component-diff --baseline-url url1 --current-url url2 --selector "button.btn-primary" [--output-dir ./diffs]`
5. `suite`:
   - `web-visual-auditor suite --baseline-url url1 --current-url url2 [--selectors "header,button,card"] [--output-dir ./reports]`

---

## 6. Diretrizes para Testes Locais Determinísticos

Para atender rigorosamente aos critérios de aceitação sem depender de internet:
1. **Researcher Tests**: Utilizar `clean_raw_html()` com fixtures HTML contendo tags propositalmente poluídas (`<script>`, `<style>`, `<svg>`), validando que o texto resultante é limpo e as tags são completamente expurgadas.
2. **DOM Auditor Tests**: Utilizar páginas HTML locais servidas via `file://` ou `data:text/html,...`. Validar que `x, y, width, height` batem exatamente com as geometrias declaradas em CSS inline.
3. **Visual Regression Tests**:
   - Criar imagens sintéticas em memória via `PIL.Image.new("RGB", (100, 100), color)`:
     - Caso 1: Duas imagens idênticas $\to$ `diff_percentage == 0.0`, `diff_pixels_count == 0`, `has_divergence == False`.
     - Caso 2: Pequena variação menor que a tolerância ($\Delta \le 15$) $\to$ `diff_percentage == 0.0`.
     - Caso 3: Divergência evidente ($\Delta > 15$, ex: quadrado azul vs vermelho de $20 \times 20$ pixels em imagem de $100 \times 100$) $\to$ `diff_pixels_count == 400`, `diff_percentage == 4.0%`, máscara possui pixels em `(255, 0, 0, 255)` na área alterada.
4. **Component Auditor Tests**: Renderizar página com múltiplos botões e cards, disparar captura por seletor, alterar cor do botão na versão v2 e comprovar que o diff é gerado apenas para o componente afetado.

---

## 7. Conclusão da Investigação Arquitetural

A arquitetura proposta garante:
- **Desacoplamento Completo**: Cada módulo tem responsabilidade única e interfaces bem definidas.
- **Tipagem Estrita**: Pydantic v2 valida contratos e garante serialização imediata para relatórios JSON/CLI.
- **Conformidade de Limites**: Tolerância $>15$, máscara `#FF0000`, `wait_until="domcontentloaded"` com fallback, `getBoundingClientRect` para nós-chave.
- **Testabilidade Total**: Módulos desacoplados permitindo testes 100% determinísticos sem internet.
