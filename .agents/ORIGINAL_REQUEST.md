# Original User Request

## 2026-09-03T03:51:58Z

Construir o pacote Python autônomo `projects/web_visual_auditor`, composto por agentes modulares para pesquisa web com extração semântica de conteúdo, inspeção hierárquica e geométrica do DOM (bounding boxes) e auditoria visual de regressão pixel a pixel (tela inteira e micro-componentes isolados de design systems).

Working directory: c:\Users\melki\meu-workspace-global\projects\web_visual_auditor
Integrity mode: development

## Requirements

### R1. Pesquisa Web & Extração Semântica de Artigos
O módulo de pesquisa deve executar consultas web estruturadas (DuckDuckGo / APIs de busca), limpar o HTML com BeautifulSoup (eliminando scripts, styles, nós svg e metadados ruidosos) e retornar referências consolidadas com títulos, URLs e snippets normalizados.

### R2. Inspeção de Geometria Computada do DOM
O módulo de inspeção deve renderizar aplicações web via Playwright em modo headless, extraindo elementos-chave (`header`, `main`, `article`, `button`, `nav`, `h1`, etc.) com IDs, classes, visibilidade computada e coordenadas geométricas precisas (`x`, `y`, `width`, `height`) obtidas via `getBoundingClientRect`.

### R3. Auditoria Visual e Regressão Diferencial Pixel a Pixel
O módulo de regressão deve comparar duas capturas de tela (baseline vs current) via Pillow (PIL), calcular o percentual exato de divergência entre imagens com tolerância a variações de antialiasing (`channel > 15`), e gerar uma imagem de máscara destacando os pixels alterados em vermelho puro (`#FF0000`).

### R4. Auditoria Granular por Micro-Componentes de Design System
O sistema deve permitir isolar seletores CSS específicos (ex: botões, cards, modais), capturando exclusivamente a área delimitada de cada componente (`element.screenshot()`), calculando suas dimensões e executando a comparação visual diferencial de forma independente da página como um todo.

### R5. Interface CLI e Módulo Integrado
O projeto deve fornecer uma interface de linha de comando (`cli.py`) e uma classe principal orquestradora (`WebVisualAuditorSuite`) permitindo disparar fluxos individuais (`search`, `dom-inspect`, `visual-diff`, `component-diff`) ou o pipeline completo.

## Verification Resources & Test Strategy

- **Testes Locais Determinísticos:** A suíte de testes deve utilizar fixtures locais (páginas HTML estáticas servidas localmente ou carregadas via `file://` / data URLs e pares de imagens baseline/current sintéticas) para testar 100% da lógica sem depender de internet ativa.
- **Suíte Pytest Completa:** Cobertura de testes unitários para a limpeza semântica de HTML, extração de geometrias do DOM, cálculo de diff de imagens e captura de micro-componentes.

## Acceptance Criteria

### Arquitetura & Qualidade de Código
- [ ] Código modular em `projects/web_visual_auditor/` estruturado em módulos independentes (`researcher.py`, `dom_auditor.py`, `visual_regression.py`, `component_auditor.py`, `cli.py`).
- [ ] Modelos de dados com dataclasses ou Pydantic tipados estritamente (`SourceReference`, `DOMNodeSummary`, `ComputedElementGeometry`, `VisualDiffResult`, `ComponentSnapshot`, `ComponentDiffReport`).
- [ ] Tratamento robusto de exceções e timeouts (uso de `wait_until="domcontentloaded"` com fallback para carregamento lento).

### Testes & Verificação
- [ ] `pytest` executado com 100% de aprovação nas fixtures locais.
- [ ] Geração comprovada do mapa diferencial (`diff_result.png` / `diff_<selector>.png`) quando há divergência visual intencional nos testes.
- [ ] Nenhum erro de lint (`ruff check .` limpo).
