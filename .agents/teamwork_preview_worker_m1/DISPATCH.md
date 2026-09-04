## 2026-09-03T03:59:39Z

Sua identidade: teamwork_preview_worker_m1
Seu diretório de trabalho: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m1
Você DEVE ler o arquivo de requisitos originais em: c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md
Leia também:
- c:\Users\melki\meu-workspace-global\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_2\survey_arch_report.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Sua missão para o Milestone M1 (Core Models & Package Scaffold):
1. Instalar as dependências necessárias no ambiente virtual uv: execute `uv add beautifulsoup4 pillow duckduckgo_search` a partir da raiz do workspace.
2. Criar a pasta `projects/web_visual_auditor` e o arquivo `projects/web_visual_auditor/pyproject.toml` configurando o pacote como autônomo com build-backend hatchling.
3. Criar `projects/web_visual_auditor/web_visual_auditor/exceptions.py` com as classes de erro especializadas (`AuditorError`, `NavigationTimeoutError`, `ElementNotFoundError`, `ImageDimensionMismatchError`, etc.).
4. Criar `projects/web_visual_auditor/web_visual_auditor/models.py` com os modelos Pydantic v2 estritos:
   - `SourceReference`: title, url, snippet, extracted_at, metadata
   - `ComputedElementGeometry`: x, y, width, height
   - `DOMNodeSummary`: tag_name, element_id, classes, text_content, is_visible, geometry
   - `VisualDiffResult`: baseline_path, current_path, diff_output_path, total_pixels, diff_pixels, diff_percentage, has_divergence
   - `ComponentSnapshot`: selector, dimensions, screenshot_path
   - `ComponentDiffReport`: selector, baseline_dimensions, current_dimensions, diff_result
   - `SuiteAuditReport`: timestamp, research_references, dom_nodes, visual_diff, component_diffs
5. Criar `projects/web_visual_auditor/web_visual_auditor/__init__.py` exportando os modelos e `__version__ = "0.1.0"`.
6. Criar `projects/web_visual_auditor/tests/test_models.py` testando validação, imutabilidade, serialização JSON dos modelos e hierarquia de exceções.
7. Executar os testes via `uv run pytest projects/web_visual_auditor/tests/test_models.py` e verificar com `uv run ruff check projects/web_visual_auditor`.
8. Gerar relatório de handoff formal em seu diretório de trabalho `c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m1\handoff.md` e enviar mensagem ao orquestrador ao concluir.
Idioma obrigatório: Português (BR).
