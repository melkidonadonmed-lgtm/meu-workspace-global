## 2026-09-11T07:15:17Z
Você é o Worker 1 responsável pelo Marco 1 (M1: Scaffold & Code Intelligence Engine) do projeto `projects/code_intelligence_agent`.
Sua pasta de trabalho exclusiva para metadados e relatórios é:
c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m1

DIRETÓRIO ALVO DO PROJETO (onde você deve escrever o código de produção e testes):
c:\Users\melki\meu-workspace-global\projects\code_intelligence_agent

ARQUIVOS DE REFERÊNCIA OBRIGATÓRIOS:
- c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md (seção ## 2026-09-11T07:05:21Z)
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_orchestrator_main_3\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_1\handoff.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_2\handoff.md

AVISO MANDATÓRIO DE INTEGRIDADE:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

SUAS TAREFAS NO MARCO 1:
1. Criar a estrutura de diretórios em `projects/code_intelligence_agent/`:
   - `app/`
   - `artifacts/grade_results/`
   - `tests/unit/`
   - `tests/integration/`
   - `tests/eval/datasets/`
2. Criar `projects/code_intelligence_agent/pyproject.toml` usando `hatchling`, dependências `google-adk>=2.9.0`, `google-antigravity`, `google-genai>=2.3.0`, `fastapi>=0.115.0`, `uvicorn>=0.30.0`, `pydantic>=2.8.0`, `typer>=0.12.0`, dev-dependencies `pytest>=8.0.0`, `ruff>=0.5.0`, e entrypoint `[project.scripts] code-intel = "app.cli:main"`.
3. Criar `projects/code_intelligence_agent/README.md` com arquitetura em Português BR e `.env.example`.
4. Implementar `projects/code_intelligence_agent/app/__init__.py`.
5. Implementar `projects/code_intelligence_agent/app/tools.py` com as ferramentas determinísticas:
   - `inspect_directory(directory_path: str, max_depth: int) -> dict[str, Any]` (com poda de pastas .git, __pycache__, .venv).
   - `read_code_file(file_path: str, start_line: int, end_line: int) -> dict[str, Any]` (leitura com linhas 1-indexed).
   - `analyze_ast_anomalies(file_path: str) -> dict[str, Any]` (análise estática via ast: sintaxe, bare except / BLE001, McCabe complexity > 10, funções > 60 linhas, chamadas perigosas).
   - `generate_unified_patch(file_path: str, original_snippet: str, replacement_snippet: str) -> dict[str, Any]` (unified diff com validação AST em dry-run antes da gravação).
   Atenção: todas as funções de ferramentas devem ter type hints estritos, NÃO ter valores default nos argumentos de ferramentas ADK, docstrings claras e retornar dicionários serializáveis em JSON.
6. Implementar `projects/code_intelligence_agent/app/agent.py`:
   - Configurar `root_agent` com ADK 2.9.0, `gemini-3.8-flash`, temperature 0.1, registro das ferramentas e rastreamento de estado em `tool_context.state`.
   - Declarar `App(name="app", root_agent=root_agent)` (convenção obrigatória do ADK).
7. Criar `projects/code_intelligence_agent/tests/conftest.py` e `tests/unit/test_tools.py`:
   - Cobertura completa de testes unitários para todas as 4 ferramentas.
   - Garantir que `generate_unified_patch` rejeite patches com erro sintático.
8. Executar verificação obrigatória no PowerShell:
   - `uv run ruff check projects/code_intelligence_agent`
   - `uv run pytest projects/code_intelligence_agent/tests/unit/test_tools.py -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"`
   Garantir 100% de sucesso nos testes e ruff 100% limpo!
