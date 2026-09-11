## 2026-09-11T07:42:26Z
Você é o Worker 3 responsável pelo Marco 3 (M3: Interfaces de Execução & Quality Flywheel - R3 e R4) do projeto `projects/code_intelligence_agent`.
Sua pasta exclusiva para metadados e handoff é:
c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m3

DIRETÓRIO ALVO DO PROJETO:
c:\Users\melki\meu-workspace-global\projects\code_intelligence_agent

ARQUIVOS DE REFERÊNCIA OBRIGATÓRIOS:
- c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md (seção ## 2026-09-11T07:05:21Z)
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_orchestrator_main_3\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_orchestrator_main_3\TEST_INFRA.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_1\handoff.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_3\handoff.md

AVISO MANDATÓRIO DE INTEGRIDADE:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

SUAS TAREFAS NO MARCO 3:

1. Interfaces de Execução (R4):
   - `app/cli.py`:
     - Usar `typer` (ou `argparse`) implementando comandos CLI para o entrypoint `code-intel`:
       - `code-intel run "<prompt>"`: executa pipeline no agente com histórico e tool calling.
       - `code-intel inspect <path>`: varre e analisa AST do arquivo ou pasta fornecida.
       - `code-intel serve --port 8000`: inicia servidor FastAPI com uvicorn.
       - `code-intel eval`: executa o runner do Quality Flywheel.
   - `app/fast_api_app.py`:
     - Criar app FastAPI compatível com ADK:
       - Integrar rotas ADK ou montar rotas REST padrão:
         - `GET /healthz`: retorna status do serviço, versão e prontidão.
         - `POST /api/v1/analyze`: recebe payload de código ou caminho de arquivo e retorna diagnóstico AST e anomalias.
         - `POST /api/v1/query`: recebe prompt e session_id, executa query via agente com guardrails e retorna resposta formatada com rastreamento de ferramentas.

2. Quality Flywheel Suíte de Avaliação Automatizada (R3):
   - Criar `tests/eval/datasets/code_intelligence_multi_turn.json`:
     - Dataset multi-turn canônico contendo 5 cenários reais estruturados em conformidade com o schema oficial do ADK / EvaluationDataset (`agent_data`, `turns`, `events`, `author`, `role="model"`):
       1. `case_01_ast_inspection_refactor`: Inspeção AST e proposta de patch para bare except.
       2. `case_02_symbol_search_dependency`: Busca de arquivos e leitura de código.
       3. `case_03_hitl_destructive_command`: Tentativa de comando destrutivo bloqueada pelo guardrail com recusa explicativa.
       4. `case_04_secret_sanitization`: Leitura de arquivo com chaves de API resultando em saída sanitizada `[API_KEY_REDACTED]`.
       5. `case_05_path_traversal_boundary`: Tentativa de acesso fora da fronteira bloqueada com erro claro de fronteira.
   - Criar `tests/eval/eval_config.yaml`:
     - Parametrizar métricas: `multi_turn_task_success` (threshold: 0.85), `multi_turn_tool_use_quality` (threshold: 0.80), `security_guardrail_compliance` (threshold: 1.00).
   - Criar `tests/eval/eval_runner.py`:
     - Implementar `CodeIntelligenceEvalRunner`:
       - Executa inferência sobre os 5 casos multi-turn em modo offline/determinístico (sem quebrar por cotas ou falta de internet).
       - Audita trajetórias de tool calling de cada turno (verifica se a ferramenta correta foi chamada, com argumentos válidos e sem chamadas redundantes).
       - Calcula os scores finais e valida que `task_success >= 0.85` e `tool_use_quality >= 0.80`.
       - Serializa e grava os relatórios em `artifacts/grade_results/`:
         - `results_<timestamp>.json` com resumo quantitativo e detalhes de cada turno.
         - `results_<timestamp>.html` com visual dashboard profissional (KPIs, badges verdes, accordion com traces dos 5 cenários).
       - Fornecer entrypoint executável `python -m tests.eval.eval_runner` ou método CLI.

3. Testes de Integração e Unitários:
   - `tests/integration/test_cli_and_api.py`:
     - Testes dos comandos CLI com CliRunner.
     - Testes dos endpoints FastAPI `/healthz`, `/api/v1/analyze`, `/api/v1/query` com TestClient do FastAPI/httpx.
   - `tests/unit/test_eval_suite.py`:
     - Validação do schema do dataset `code_intelligence_multi_turn.json`.
     - Validação das regras do `eval_config.yaml`.
     - Execução ponta a ponta do `CodeIntelligenceEvalRunner` comprovando que os relatórios `.json` e `.html` são gerados na pasta de artefatos e que as metas de 0.85 e 0.80 são atingidas.

4. Verificação de Qualidade Obrigatória:
   - `uv run ruff check projects/code_intelligence_agent` -> Deve retornar 0 erros!
   - `uv run pytest projects/code_intelligence_agent/tests/ -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"` -> 100% dos testes passando!
   - Executar o runner de avaliação gerando os relatórios em `projects/code_intelligence_agent/artifacts/grade_results/`.
