# DISPATCH — teamwork_preview_worker_m4

## 2026-09-03T04:05:07Z
Sua identidade: teamwork_preview_worker_m4
Seu diretório de trabalho: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m4
Você DEVE ler o arquivo de requisitos originais em: c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md
Leia também:
- c:\Users\melki\meu-workspace-global\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_2\survey_arch_report.md
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\models.py
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\tests\fixtures\image_fixtures.py

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Sua missão para o Milestone M4 (Visual Regression Engine & Component Auditor):
1. Arquivos de sua propriedade exclusiva:
   - `projects/web_visual_auditor/web_visual_auditor/visual_regression.py`
   - `projects/web_visual_auditor/web_visual_auditor/component_auditor.py`
   - `projects/web_visual_auditor/tests/test_visual_regression.py`
   - `projects/web_visual_auditor/tests/test_component_auditor.py`
2. Implementar `visual_regression.py` com:
   - `VisualRegressionAuditor`: comparação de capturas de tela (baseline vs current) via Pillow (PIL) com fallback puro caso PIL não esteja instalado.
   - Algoritmo diferencial pixel a pixel com tolerância: um pixel difere se max(|R1-R2|, |G1-G2|, |B1-B2|) > 15 (tolerância padrão de canal = 15).
   - Variações com delta <= 15 NÃO contam como divergência.
   - Geração de imagem de máscara destacando os pixels alterados em vermelho puro `#FF0000` ((255, 0, 0, 255) ou (255, 0, 0)), salvando em `diff_result.png` (ou caminho fornecido).
   - Cálculo do percentual exato de divergência: `(diff_pixels / total_pixels) * 100.0`.
   - Tratamento de dimensões incompatíveis (disparando `ImageDimensionMismatchError`).
   - Retornar modelo `VisualDiffResult`.
3. Implementar `component_auditor.py` com:
   - `ComponentAuditor`: auditoria granular por micro-componentes de design system isolados por seletores CSS específicos (ex: botões, cards, modais).
   - Captura isolada da área delimitada via `element.screenshot()` com Playwright/Patchright (ou recorte por bounding box em imagem de tela com fallback).
   - Comparação diferencial do componente gerando `diff_<selector_sanitized>.png`.
   - Retornar `ComponentSnapshot` e `ComponentDiffReport`.
4. Criar `tests/test_visual_regression.py` e `tests/test_component_auditor.py` testando:
   - Comparação de imagens idênticas (0% diff).
   - Antialiasing com ruído <= 15 (0% diff, 0 pixels alterados).
   - Divergência controlada com quadrado 20x20 sobre 100x100 comprovando exatamente 400 pixels divergentes = 4.00% e geração comprovada de `diff_result.png` com pixel vermelho #FF0000.
   - Auditoria por componente gerando `diff_<selector>.png`.
5. Executar os testes via pytest e verificar com ruff check.
6. Gerar handoff.md formal em seu diretório de trabalho e enviar mensagem ao orquestrador ao concluir.
Idioma obrigatório: Português (BR).
