## 2026-09-03T04:05:07Z
Sua identidade: teamwork_preview_worker_m3
Seu diretório de trabalho: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m3
Você DEVE ler o arquivo de requisitos originais em: c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md
Leia também:
- c:\Users\melki\meu-workspace-global\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_2\survey_arch_report.md
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\models.py

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Sua missão para o Milestone M3 (DOM Geometry Inspector):
1. Arquivos de sua propriedade exclusiva:
   - `projects/web_visual_auditor/web_visual_auditor/dom_auditor.py`
   - `projects/web_visual_auditor/tests/test_dom_auditor.py`
2. Implementar `dom_auditor.py` com:
   - Classe `DOMAuditor` suportando renderização headless com Playwright (adotar import dual adaptativo `try: from playwright.sync_api import sync_playwright ... except ImportError: from patchright.sync_api import sync_playwright`).
   - Navegação robusta com `wait_until="domcontentloaded"` e tratamento de timeout com fallback para permitir inspeção em páginas ricas ou offline.
   - Extração precisa dos nós-chave: `header`, `main`, `article`, `button`, `nav`, `h1` e outros seletores configuráveis.
   - Extração geométrica via `getBoundingClientRect` (`x`, `y`, `width`, `height`), `id`, `classes`, `text_content` e visibilidade computada (`is_visible`).
   - Método `inspect_url(url)` e `inspect_html(html_content)` (suportando data URLs ou carregamento direto para testes 100% locais).
   - Prover fallback resiliente para parsing de nós estruturais caso o browser headless não consiga ser disparado no ambiente.
   - Retornar instâncias tipadas de `DOMNodeSummary` e `ComputedElementGeometry`.
3. Criar `projects/web_visual_auditor/tests/test_dom_auditor.py` cobrindo:
   - Inspeção determinística usando a fixture `sample_page.html`.
   - Detecção dos elementos obrigatórios (`header`, `main`, `article`, `button`, `nav`, `h1`).
   - Validação dos valores de geometria (`x`, `y`, `width`, `height`) e visibilidade.
   - Tratamento correto de exceções e timeouts.
4. Executar os testes via pytest e verificar com ruff check.
5. Gerar handoff.md formal em seu diretório de trabalho e enviar mensagem ao orquestrador ao concluir.
Idioma obrigatório: Português (BR).
