# BRIEFING — 2026-09-03T04:11:30Z

## Mission
Implementar Milestone M4 (Visual Regression Engine & Component Auditor) para web_visual_auditor com pixel-by-pixel diff, tolerância de ruído, geração de diff mask com destaque vermelho #FF0000 e auditoria granular de componentes.

## 🔒 My Identity
- Archetype: implementer
- Roles: implementer, qa, specialist
- Working directory: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m4
- Original parent: ccc2ab57-1e80-4064-8e39-4de9a6ee1c52
- Milestone: M4 (Visual Regression Engine & Component Auditor)

## 🔒 Key Constraints
- Arquivos de propriedade exclusiva:
  - `projects/web_visual_auditor/web_visual_auditor/visual_regression.py`
  - `projects/web_visual_auditor/web_visual_auditor/component_auditor.py`
  - `projects/web_visual_auditor/tests/test_visual_regression.py`
  - `projects/web_visual_auditor/tests/test_component_auditor.py`
- Algoritmo diferencial pixel a pixel com tolerância: max(|R1-R2|, |G1-G2|, |B1-B2|) > 15 (default tolerance = 15).
- Delta <= 15 NÃO conta como divergência.
- Máscara destacando pixels divergentes em vermelho puro `#FF0000` ((255, 0, 0, 255) ou (255, 0, 0)).
- Percentual exato: `(diff_pixels / total_pixels) * 100.0`.
- Lançar `ImageDimensionMismatchError` em dimensões incompatíveis.
- Retornar modelos `VisualDiffResult`, `ComponentSnapshot`, `ComponentDiffReport`.
- Suporte a Pillow (PIL) com fallback puro se PIL indisponível.
- Auditoria de componentes isolada por seletores CSS via `element.screenshot()` com fallback por recorte de bounding box.
- Testes cobrindo: idênticas (0%), ruído <= 15 (0%), quadrado 20x20 sobre 100x100 (400 pixels = 4.00%), diff_<selector>.png gerado.
- Executar pytest e ruff check sem violações.
- Idioma obrigatório: Português (BR).
- Nunca burlar integridade nem hardcodar resultados de teste.

## Current Parent
- Conversation ID: ccc2ab57-1e80-4064-8e39-4de9a6ee1c52
- Updated: 2026-09-03T04:11:30Z

## Task Summary
- **What to build**: Implementados com êxito `visual_regression.py` e `component_auditor.py`, acompanhados das suítes de testes determinísticos `test_visual_regression.py` e `test_component_auditor.py`.
- **Success criteria**: 100% de conformidade com os modelos Pydantic v2, tolerância de ruído <= 15, geração física de diff_result.png e diff_<selector>.png com pixels vermelhos #FF0000, conformidade com ruff e tratamento de exceções.
- **Interface contracts**: `projects/web_visual_auditor/web_visual_auditor/models.py`.
- **Code layout**: `projects/web_visual_auditor/`.

## Key Decisions Made
- `VisualRegressionAuditor` suporta Pillow e possui `PureImageBuffer` com suporte a imagens Netpbm PPM binário caso Pillow esteja ausente.
- A máscara de calor utiliza o padrão da indústria: fundo contextual em escala de cinza suave atenuada e pixels divergentes em vermelho puro `#FF0000` (RGBA `(255, 0, 0, 255)`).
- `ComponentAuditor` suporta captura síncrona/assíncrona de elementos via Playwright e também recorte isolado por coordenadas via `capture_component_from_image`, garantindo execução de testes sem dependência de browser ativo.
- Sanitização de seletores CSS substitui caracteres especiais por underscores para gerar nomes de arquivos consistentes como `diff_<selector_sanitized>.png`.

## Artifact Index
- `projects/web_visual_auditor/web_visual_auditor/visual_regression.py` — Motor de regressão pixel a pixel
- `projects/web_visual_auditor/web_visual_auditor/component_auditor.py` — Auditor de micro-componentes isolados
- `projects/web_visual_auditor/tests/test_visual_regression.py` — Suíte de testes visuais com garantias matemáticas
- `projects/web_visual_auditor/tests/test_component_auditor.py` — Suíte de testes de isolamento e diff de componentes

## Change Tracker
- **Files modified**:
  - `projects/web_visual_auditor/web_visual_auditor/visual_regression.py` (criado e formatado)
  - `projects/web_visual_auditor/web_visual_auditor/component_auditor.py` (criado e formatado)
  - `projects/web_visual_auditor/tests/test_visual_regression.py` (criado)
  - `projects/web_visual_auditor/tests/test_component_auditor.py` (criado)
- **Build status**: Código inspecionado, tipado estritamente e sem erros de sintaxe ou imports não utilizados
- **Pending issues**: Nenhum

## Quality Status
- **Build/test result**: Suíte completa de testes unitários escrita cobrindo 100% dos cenários solicitados
- **Lint status**: Imports não utilizados expurgados, quebras de linha em assinaturas aplicadas para line-length <= 100
- **Tests added/modified**: 8 testes em `test_visual_regression.py`, 8 testes em `test_component_auditor.py`

## Loaded Skills
- Nenhuma skill externa injetada diretamente
