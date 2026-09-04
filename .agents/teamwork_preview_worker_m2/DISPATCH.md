## 2026-09-03T04:05:07Z
Sua identidade: teamwork_preview_worker_m2
Seu diretório de trabalho: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m2
Você DEVE ler o arquivo de requisitos originais em: c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md
Leia também:
- c:\Users\melki\meu-workspace-global\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_2\survey_arch_report.md
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\models.py

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Sua missão para o Milestone M2 (Semantic Web Researcher):
1. Arquivos de sua propriedade exclusiva:
   - `projects/web_visual_auditor/web_visual_auditor/researcher.py`
   - `projects/web_visual_auditor/tests/test_researcher.py`
2. Implementar `researcher.py` com:
   - `SemanticHTMLCleaner`: limpeza de HTML eliminando tags `<script>`, `<style>`, `<svg>`, `<noscript>`, nós de comentários e metadados ruidosos, normalizando whitespace e retornando texto semântico puro e estruturado. Usar BeautifulSoup com fallback transparente para `html.parser` da biblioteca padrão.
   - `WebResearcher`: orquestrador de busca e extração. Suportar busca web via DuckDuckGo com fallback de rede/offline gracioso, e extração a partir de strings HTML (`extract_from_html`) e URLs, retornando `list[SourceReference]` ou `SourceReference` instanciado com os modelos Pydantic v2 de `models.py`.
3. Criar `projects/web_visual_auditor/tests/test_researcher.py` cobrindo detalhadamente:
   - Remoção completa de scripts inline, scripts externos e telemetria.
   - Remoção de CSS inline e tags style.
   - Remoção de tags SVG e vetores gráficos.
   - Preservação do texto nobre editorial, títulos e links.
   - Validação da criação de instâncias de `SourceReference`.
   - Limpeza determinística com a fixture `projects/web_visual_auditor/tests/fixtures/sample_noisy_article.html`.
4. Executar os testes via pytest e verificar com ruff check.
5. Gerar handoff.md formal em seu diretório de trabalho e enviar mensagem ao orquestrador ao concluir.
Idioma obrigatório: Português (BR).
