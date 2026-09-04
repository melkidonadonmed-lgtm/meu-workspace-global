## 2026-09-03T04:12:19Z

Sua identidade: teamwork_preview_worker_m5
Seu diretório de trabalho: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m5
Você DEVE ler o arquivo de requisitos originais em: c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md
Leia também:
- c:\Users\melki\meu-workspace-global\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_2\survey_arch_report.md
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\models.py
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\researcher.py
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\dom_auditor.py
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\visual_regression.py
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\component_auditor.py

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Sua missão para o Milestone M5 (Suite Orchestrator & CLI):
1. Arquivos de sua propriedade exclusiva:
   - `projects/web_visual_auditor/web_visual_auditor/suite.py`
   - `projects/web_visual_auditor/web_visual_auditor/cli.py`
   - `projects/web_visual_auditor/tests/test_suite_cli.py`
   - (atualização pontual de `projects/web_visual_auditor/web_visual_auditor/__init__.py` para expor `WebVisualAuditorSuite`)
2. Implementar `suite.py`:
   - Classe `WebVisualAuditorSuite`: integra `WebResearcher`, `DOMAuditor`, `VisualRegressionAuditor` e `ComponentAuditor`.
   - Métodos individuais de fluxo: `run_semantic_research(query, limit)`, `clean_article_html(raw_html, url)`, `run_dom_audit(url_or_html)`, `run_visual_audit(baseline, current, diff_out, tolerance)`, `run_component_audit(baseline, current, selectors, diff_dir)`.
   - Método integrado `run_full_suite(config: SuiteConfig | dict) -> SuiteAuditReport`.
3. Implementar `cli.py`:
   - Interface de linha de comando modular com `argparse` suportando os 5 subcomandos canônicos exigidos no Requisito R5:
     `search`, `dom-inspect`, `visual-diff`, `component-diff`, `suite`.
   - Suporte a flags `--json`, `--output`, `--diff-out`, `--tolerance`, `--selectors` e códigos de saída POSIX limpos (0 = sucesso/sem divergência, 1 = divergência visual detectada ou erro).
   - Função `main(argv=None)` chamável programaticamente.
4. Implementar `tests/test_suite_cli.py`:
   - Testar exaustivamente cada método de `WebVisualAuditorSuite` com fixtures locais determinísticas.
   - Testar a execução da CLI invocando os 5 subcomandos com argumentos válidos e argumentos de erro, validando os códigos de saída e a formatação JSON/texto.
5. Executar os testes via pytest e verificar com ruff check.
6. Gerar handoff.md formal em seu diretório de trabalho e enviar mensagem ao orquestrador ao concluir.
Idioma obrigatório: Português (BR).
