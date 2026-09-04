# Project: web_visual_auditor

## Architecture
O pacote `projects/web_visual_auditor` é uma biblioteca autônoma em Python 3.11+ para pesquisa semântica, inspeção geométrica de DOM e auditoria visual diferencial pixel a pixel (tela inteira e micro-componentes).

```
projects/web_visual_auditor/
├── pyproject.toml
├── README.md
├── web_visual_auditor/
│   ├── __init__.py
│   ├── models.py               # Modelos Pydantic v2 estritos
│   ├── exceptions.py           # Hierarquia de exceções especializadas
│   ├── researcher.py           # R1: Extração semântica e limpeza HTML
│   ├── dom_auditor.py          # R2: Playwright headless e geometria DOM
│   ├── visual_regression.py    # R3: Regressão pixel a pixel (Pillow)
│   ├── component_auditor.py    # R4: Auditoria de micro-componentes CSS
│   ├── suite.py                # R5: WebVisualAuditorSuite integrada
│   └── cli.py                  # R5: CLI unificada argparse
└── tests/
    ├── fixtures/               # HTML estático e imagens sintéticas
    ├── test_researcher.py
    ├── test_dom_auditor.py
    ├── test_visual_regression.py
    ├── test_component_auditor.py
    ├── test_suite_cli.py
    └── test_e2e.py
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Pydantic Models & Exceptions | Modelos tipados estritos (SourceReference, DOMNodeSummary, ComputedElementGeometry, VisualDiffResult, ComponentSnapshot, ComponentDiffReport) e hierarquia de erros | M1 | survey_arch_report.md |
| 2 | Semantic HTML Cleaning | Remoção cirúrgica de script, style, svg, nós noscript, comentários e metadados ruidosos | M2 | ORIGINAL_REQUEST §R1 |
| 3 | Web Search & Reference Normalization | Execução de consultas estruturadas e normalização de SourceReference (título, url, snippet) | M2 | ORIGINAL_REQUEST §R1 |
| 4 | Playwright Headless Rendering | Renderização headless robusta com wait_until="domcontentloaded" e fallback de timeout | M3 | ORIGINAL_REQUEST §R2 |
| 5 | DOM Key Elements & Geometry Extraction | Extração de header, main, article, button, nav, h1 e getBoundingClientRect (x, y, width, height, id, classes, visibilidade) | M3 | ORIGINAL_REQUEST §R2 |
| 6 | Pixel-by-Pixel Visual Regression | Comparação PIL, tolerância de canal > 15, cálculo de percentual exato | M4 | ORIGINAL_REQUEST §R3 |
| 7 | Heatmap Mask Generation | Geração de máscara destacando divergências em vermelho puro #FF0000 e salvando diff_result.png | M4 | ORIGINAL_REQUEST §R3 |
| 8 | Micro-Component CSS Isolation | Isolamento de seletores CSS, element.screenshot() e dimensões de componente | M4 | ORIGINAL_REQUEST §R4 |
| 9 | Component Differential Audit | Comparação visual independente por componente gerando diff_<selector>.png | M4 | ORIGINAL_REQUEST §R4 |
| 10 | Unified CLI Interface | Subcomandos search, dom-inspect, visual-diff, component-diff, suite | M5 | ORIGINAL_REQUEST §R5 |
| 11 | WebVisualAuditorSuite Orchestrator | Classe orquestradora executando pipelines modulares ou integrados | M5 | ORIGINAL_REQUEST §R5 |
| 12 | Deterministic Offline Test Suite | 100% dos testes determinísticos com fixtures locais e imagens sintéticas | M6 | ORIGINAL_REQUEST §Acceptance |
| 13 | Code Quality & Lint Cleanliness | Conformidade com ruff check limpo e tipagem Python 3.11+ | M6 | ORIGINAL_REQUEST §Acceptance |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Core Models & Package Scaffold | Modelos Pydantic v2, exceções e pyproject.toml autônomo | none | DONE |
| M2 | Semantic Web Researcher | Módulo researcher.py com limpeza semântica e suporte offline | M1 | DONE |
| M3 | DOM Geometry Inspector | Módulo dom_auditor.py com Playwright headless e bounding boxes | M1 | DONE |
| M4 | Visual Regression & Component Auditor | Módulos visual_regression.py e component_auditor.py (diff, máscara #FF0000) | M1 | DONE |
| M5 | Suite Orchestrator & CLI | Módulos suite.py e cli.py com subcomandos e orquestração | M2, M3, M4 | DONE |
| M6 | Final Milestone: E2E Tests & Hardening | 100% aprovação no pytest, diff_result.png gerado e ruff check limpo | M1, M2, M3, M4, M5 | DONE |

## Interface Contracts

### researcher.py ↔ models.py
```python
class SemanticHTMLCleaner:
    def clean_html(self, raw_html: str, base_url: str = "") -> tuple[str, list[SourceReference]]: ...

class WebResearcher:
    def search_and_extract(self, query: str, limit: int = 5) -> list[SourceReference]: ...
    def extract_from_html(self, raw_html: str, url: str = "local://raw") -> SourceReference: ...
```

### dom_auditor.py ↔ models.py
```python
class DOMAuditor:
    def inspect_url(self, url: str) -> list[DOMNodeSummary]: ...
    def inspect_html(self, html_content: str) -> list[DOMNodeSummary]: ...
```

### visual_regression.py ↔ models.py
```python
class VisualRegressionAuditor:
    def compare_images(
        self,
        baseline_img: Image.Image | str | Path,
        current_img: Image.Image | str | Path,
        diff_output_path: str | Path | None = None,
        tolerance: int = 15,
    ) -> VisualDiffResult: ...
```

### component_auditor.py ↔ models.py & visual_regression.py
```python
class ComponentAuditor:
    def capture_component(self, url_or_html: str, selector: str) -> ComponentSnapshot: ...
    def audit_component(
        self,
        baseline_url_or_html: str,
        current_url_or_html: str,
        selector: str,
        diff_output_dir: str | Path = ".",
    ) -> ComponentDiffReport: ...
```

### suite.py & cli.py ↔ todos os módulos
```python
class WebVisualAuditorSuite:
    def run_semantic_research(self, query: str) -> list[SourceReference]: ...
    def run_dom_audit(self, url_or_html: str) -> list[DOMNodeSummary]: ...
    def run_visual_audit(self, baseline: str | Path, current: str | Path, diff_out: str | Path | None = None) -> VisualDiffResult: ...
    def run_component_audit(self, baseline: str, current: str, selectors: list[str], diff_dir: str | Path = ".") -> list[ComponentDiffReport]: ...
    def run_full_suite(self, config: SuiteConfig) -> SuiteAuditReport: ...
```

## Code Layout
- Package: `c:\Users\melki\meu-workspace-global\projects\web_visual_auditor`
- Package source: `projects/web_visual_auditor/web_visual_auditor/`
- Test source: `projects/web_visual_auditor/tests/`
- Test fixtures: `projects/web_visual_auditor/tests/fixtures/`
