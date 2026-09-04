# Relatório de Diagnóstico e Survey de Ambiente: `web_visual_auditor`

**Data da Auditoria:** 2026-09-03T03:58:00Z  
**Auditor / Explorer:** `teamwork_preview_explorer_survey_1`  
**Workspace Base:** `c:\Users\melki\meu-workspace-global`  
**Destino do Projeto:** `c:\Users\melki\meu-workspace-global\projects\web_visual_auditor`  

---

## 1. Resumo Executivo

O presente diagnóstico foi conduzido para averiguar as condições do ambiente de desenvolvimento, integridade do workspace, configuração do Python/`uv`, disponibilidade de executáveis de teste e análise estática (`pytest`, `ruff`), estado dos módulos de automação web (`playwright`/`patchright` e Chromium headless), e as bibliotecas necessárias para a concepção do pacote `projects/web_visual_auditor`.

### Principais Conclusões:
1. **Inexistência Prévia do Módulo:** O diretório `c:\Users\melki\meu-workspace-global\projects` ainda não existe fisicamente na raiz do repositório. O pacote autônomo `projects/web_visual_auditor` deverá ser inicializado do zero com sua própria arquitetura modular.
2. **Ambiente Python Atualizado:** O ambiente virtual ativo (`.venv`) opera com **Python 3.12.10** (AMD64 64-bit no Windows 11), atendendo plenamente à especificação `>=3.11`.
3. **Ferramental de Qualidade Disponível:** `pytest` (9.1.1), `pytest-asyncio` (1.4.0), `pytest-cov` (7.1.0) e `ruff` (0.16.5) estão prontos para uso no ambiente.
4. **Infraestrutura de Browser Pronta:** O navegador **Chromium Headless** (`chromium-1234` e `chromium_headless_shell-1234`) já se encontra baixado em `C:\Users\melki\AppData\Local\ms-playwright`. O pacote `patchright` (1.55.2 — fork stealth 100% compatível com a API Playwright) está instalado em `site-packages`.
5. **Gaps de Bibliotecas no `.venv`:** `beautifulsoup4`, `pillow` e `duckduckgo_search` não estão instalados no ambiente virtual principal. O pacote deve declará-las explicitamente em seu `pyproject.toml` / dependências e oferecer fallbacks/mocks adequados nas suítes de testes determinísticos.
6. **Políticas de Execução Windows:** Comandos interativos de shell podem disparar prompts de permissão com timeout de 60s. O código de testes deve operar com fixtures locais estáticas (`file:///` e data URLs) sem requisições HTTP externas ativas.

---

## 2. Diagnóstico da Estrutura do Workspace

### 2.1 Estado da Raiz (`c:\Users\melki\meu-workspace-global`)
O repositório é governado pelas especificações em `AGENTS.md`, `GEMINI.md` e `pyproject.toml`.
- **Raiz do Projeto:**
  - `agents/`: Orquestradores centrais e agentes especializados.
  - `skills/`: Catálogo modular de habilidades com progressive disclosure.
  - `mcp_servers/`: Servidores FastMCP (stdio / SSE).
  - `shared/`: Persistência SQLite WAL, circuit breaker, autenticação.
  - `configs/`: Guardrails Zero-Trust (`guardrails.yaml`), manifestos.
  - `tests/`: Suíte global de testes unitários e de integração.
  - `.venv/`: Ambiente virtual principal gerenciado por `uv`.
- **Diretório `projects/`:**
  - Status atual: **Não existente**.
  - No `AGENTS.md`, projetos externos históricos apontavam para `Brain/projetos/` (`pcm`, `canvas_ide`, `keepdocs-workspace`).
  - No `GEMINI.md` e no `ORIGINAL_REQUEST.md`, o padrão para novos subprojetos de clientes e ferramentas autônomas é residir sob `projects/<nome_do_projeto>`.
  - Portanto, a criação de `projects/web_visual_auditor/` deve criar o diretório `projects/` como container de projetos autônomos.

### 2.2 Configurações Existentes
- **`pyproject.toml` da Raiz:**
  - Versão: 1.0.0
  - Python: `>=3.11`
  - Dependências raiz: `google-genai`, `fastmcp`, `fastapi`, `uvicorn`, `pydantic`, `pyyaml`, `python-dotenv`, `httpx`, `rich`, `opentelemetry-api`, `opentelemetry-sdk`.
  - Dependências dev: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`.
  - `tool.ruff`: `line-length = 100`, `target-version = "py311"`, `extend-exclude = ["skills/research/notebooklm", "inbox", ".agents"]`.
  - `tool.pytest.ini_options`: `asyncio_mode = "auto"`, `testpaths = ["tests"]`, `pythonpath = ["."]`.

---

## 3. Inventário de Ferramentas, Binários e Ambiente Virtual

A tabela abaixo detalha o status e a localização exata de cada componente do ambiente:

| Ferramenta / Binário | Versão Detectada | Localização no Sistema de Arquivos | Status |
| :--- | :--- | :--- | :--- |
| **uv** | UV CLI | `C:\Users\melki\.local\bin\uv.exe` | ✅ Instalado |
| **Python** | 3.12.10 (AMD64) | `c:\Users\melki\meu-workspace-global\.venv\Scripts\python.exe` | ✅ Instalado (`pyvenv.cfg`) |
| **pytest** | 9.1.1 | `c:\Users\melki\meu-workspace-global\.venv\Scripts\pytest.exe` | ✅ Instalado |
| **pytest-asyncio** | 1.4.0 | `.venv\Lib\site-packages\pytest_asyncio-1.4.0.dist-info` | ✅ Instalado |
| **pytest-cov** | 7.1.0 | `.venv\Lib\site-packages\pytest_cov-7.1.0.dist-info` | ✅ Instalado |
| **ruff** | 0.16.5 | `c:\Users\melki\meu-workspace-global\.venv\Scripts\ruff.exe` | ✅ Instalado |
| **mypy** | 1.11+ | `c:\Users\melki\meu-workspace-global\.venv\Scripts\mypy.exe` | ✅ Instalado |
| **patchright (Playwright Fork)** | 1.55.2 | `c:\Users\melki\meu-workspace-global\.venv\Lib\site-packages\patchright` | ✅ Instalado |
| **Chromium Headless** | 1234 | `C:\Users\melki\AppData\Local\ms-playwright\chromium-1234` | ✅ Baixado & Pronto |
| **Chromium Headless Shell** | 1234 | `C:\Users\melki\AppData\Local\ms-playwright\chromium_headless_shell-1234` | ✅ Baixado & Pronto |
| **httpx** | 0.28.1 | `.venv\Lib\site-packages\httpx-0.28.1.dist-info` | ✅ Instalado |
| **requests** | 2.34.2 | `.venv\Lib\site-packages\requests-2.34.2.dist-info` | ✅ Instalado |
| **pydantic** | 2.13.5 | `.venv\Lib\site-packages\pydantic-2.13.5.dist-info` | ✅ Instalado |
| **fastapi** | 0.141.1 | `.venv\Lib\site-packages\fastapi-0.141.1.dist-info` | ✅ Instalado |
| **beautifulsoup4 (bs4)** | — | Ausente em `.venv\Lib\site-packages` | ⚠️ Requer instalação / fallback |
| **pillow (PIL)** | — | Ausente em `.venv\Lib\site-packages` | ⚠️ Requer instalação / fallback |
| **duckduckgo_search** | — | Ausente em `.venv\Lib\site-packages` | ⚠️ Requer instalação / mock |

---

## 4. Análise do Motor de Browser (Playwright vs Patchright)

### 4.1 A Descoberta do Patchright
No ambiente virtual, encontramos o pacote `patchright` 1.55.2 instalado. O Patchright é um drop-in replacement anti-detect do Playwright que mantém exatamente as mesmas interfaces:
- `patchright.sync_api` (`sync_playwright`, `Page`, `Browser`, etc.)
- `patchright.async_api` (`async_playwright`)
- Bounding Box: `element.bounding_box()` e `element.evaluate("el => el.getBoundingClientRect()")`
- Screenshots de elementos: `element.screenshot(path=...)`

### 4.2 Navegadores Físicos Disponíveis
Em `C:\Users\melki\AppData\Local\ms-playwright`, os binários de Chromium já estão presentes (`chromium-1234`, `chromium_headless_shell-1234`, `ffmpeg-1011`, `winldd-1007`). Portanto, chamadas headless do Playwright/Patchright funcionarão localmente sem exigir download em tempo de execução.

### 4.3 Estratégia de Resiliência no Código
Para atender perfeitamente aos requisitos e permitir portabilidade total, os módulos `dom_auditor.py` e `component_auditor.py` devem adotar o seguinte padrão de importação universal:
```python
try:
    from playwright.sync_api import Browser, Locator, Page, sync_playwright
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
except ImportError:
    try:
        from patchright.sync_api import Browser, Locator, Page, sync_playwright
        from patchright.sync_api import TimeoutError as PlaywrightTimeoutError
    except ImportError:
        sync_playwright = None
        Page = None
```
Desta forma, o sistema funciona perfeitamente tanto se `playwright` for instalado quanto com o `patchright` já presente.

---

## 5. Mapeamento com os Requisitos do ORIGINAL_REQUEST.md

| Requisito | Descrição | Status no Ambiente | Diretriz de Implementação & Mitigação |
| :--- | :--- | :--- | :--- |
| **R1. Pesquisa Web & Extração Semântica** | DuckDuckGo / APIs busca, limpeza HTML com BeautifulSoup4, extração de títulos, URLs e snippets. | `httpx` e `requests` disponíveis. `duckduckgo_search` e `bs4` ausentes no `.venv`. | O módulo `researcher.py` deve utilizar `httpx`/`requests` com suporte opcional a `duckduckgo_search` e fallback para DuckDuckGo HTML Lite ou APIs REST. Para parsing, suporte a `bs4` com fallback interno para o parser padrão `html.parser` da biblioteca padrão Python (`from html.parser import HTMLParser`), garantindo funcionamento mesmo sem bibliotecas externas instaladas. |
| **R2. Inspeção de Geometria do DOM** | Renderização headless via Playwright/Patchright, extração de elementos (`header`, `main`, `button`, etc.), coordenadas `getBoundingClientRect`. | Patchright 1.55.2 e Chromium 1234 disponíveis. | O módulo `dom_auditor.py` utilizará a API Playwright/Patchright headless com `getBoundingClientRect()` para obter `x`, `y`, `width`, `height`. Fallback com mock / parsing estático para testes offline determinísticos. |
| **R3. Auditoria Visual & Regressão Pixel a Pixel** | Comparação baseline vs current via Pillow, tolerância a antialiasing (`channel > 15`), máscara com `#FF0000`. | Pillow não instalado no `.venv`. | O módulo `visual_regression.py` deve ser implementado com interface Pillow (`PIL.Image`). Adicionalmente, fornecer um motor leve nativo em Python puro / array numérico para cálculo de divergência e geração de bitmap/PNG caso Pillow não esteja instalado ou durante testes unitários isolados. |
| **R4. Auditoria Granular por Micro-Componentes** | Isolamento de seletores CSS (`element.screenshot()`), cálculo dimensional e comparação diferencial isolada. | Suportado nativamente via Locator Playwright/Patchright (`locator.screenshot()`). | `component_auditor.py` orquestra seletores específicos (ex: `button.primary`, `.card`, `#navbar`), capturando o buffer e despachando para o motor de diff de R3. |
| **R5. CLI e Módulo Integrado** | `cli.py` e `WebVisualAuditorSuite` permitindo fluxos individuais (`search`, `dom-inspect`, `visual-diff`, `component-diff`) ou pipeline completo. | Suportado nativamente via `argparse` ou `sys.argv`. | Implementar CLI rica, com saída formatada e código de retorno padronizado (`0` para sucesso, `1` para falha/divergência acima do threshold). |

---

## 6. Restrições do Ambiente Windows PowerShell & Diretrizes Técnicas

1. **Manipulação de Caminhos (Windows Backslash vs Unix Slash):**
   - **Regra:** Utilizar estritamente `pathlib.Path` para manipulação de diretórios e arquivos em todos os módulos.
   - **Evitar:** Concatenação manual de strings com `"/"` ou `"\\"`.
   - **URLs Locais:** Ao passar caminhos de arquivos para navegadores (Playwright), converter usando `path.resolve().as_uri()` para gerar URIs compatíveis com `file:///C:/...`.

2. **Isolamento de Testes Determinísticos (Sem Internet):**
   - Conforme o `ORIGINAL_REQUEST.md`:
     > "A suíte de testes deve utilizar fixtures locais (páginas HTML estáticas servidas localmente ou carregadas via file:// / data URLs e pares de imagens baseline/current sintéticas) para testar 100% da lógica sem depender de internet ativa."
   - Os testes unitários devem incluir:
     - Páginas de teste em HTML estático (com botões, headers, modais e layouts conhecidos).
     - Data URLs (`data:text/html,...`) para testes instantâneos sem I/O de disco.
     - Imagens sintéticas de baseline e current (geradas proceduralmente com e sem divergência intencional de pixels para validação da máscara `#FF0000`).

3. **Compatibilidade com Linter e Formatação:**
   - O repositório utiliza `ruff check .` com `line-length = 100` e `target-version = "py311"`.
   - Todo código novo deve seguir tipagem estrita (`dataclasses` ou `pydantic`), docstrings em Português (BR) e conforms estrito ao Ruff.

---

## 7. Próximos Passos Recomendados para a Equipe de Engenharia

1. **Criação da Estrutura de Pastas:**
   ```text
   c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\
   ├── pyproject.toml
   ├── README.md
   ├── web_visual_auditor/
   │   ├── __init__.py
   │   ├── models.py
   │   ├── researcher.py
   │   ├── dom_auditor.py
   │   ├── visual_regression.py
   │   ├── component_auditor.py
   │   ├── suite.py
   │   └── cli.py
   └── tests/
       ├── __init__.py
       ├── conftest.py
       ├── test_researcher.py
       ├── test_dom_auditor.py
       ├── test_visual_regression.py
       ├── test_component_auditor.py
       └── test_cli.py
   ```
2. **Definição dos Modelos em `models.py`:**
   - `SourceReference(title, url, snippet, date_crawled)`
   - `ComputedElementGeometry(selector, tag_name, x, y, width, height, is_visible)`
   - `DOMNodeSummary(tag, element_id, classes, text_content, geometry)`
   - `VisualDiffResult(baseline_path, current_path, diff_path, total_pixels, divergent_pixels, diff_ratio, is_identical)`
   - `ComponentSnapshot(selector, bounding_box, screenshot_bytes, local_path)`
   - `ComponentDiffReport(selector, diff_result, metadata)`

Este relatório fornece a base empírica completa para a fase de arquitetura e implementação.
