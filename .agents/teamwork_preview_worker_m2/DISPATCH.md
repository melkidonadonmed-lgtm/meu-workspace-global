## 2026-09-11T07:32:48Z
Você é o Worker 2 do projeto `projects/code_intelligence_agent`.
Sua pasta de trabalho para metadados e handoff é:
c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m2

DIRETÓRIO ALVO DO PROJETO:
c:\Users\melki\meu-workspace-global\projects\code_intelligence_agent

ARQUIVOS DE LEITURA OBRIGATÓRIA:
- c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md (seção ## 2026-09-11T07:05:21Z)
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_orchestrator_main_3\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_reviewer_m1\handoff.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_challenger_m1\handoff.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_2\handoff.md

AVISO MANDATÓRIO DE INTEGRIDADE:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

SUAS MISSÕES:

PARTE 1 — CORREÇÕES PONTUAIS DE M1 (solicitadas pelo Reviewer 1 e Challenger 1):
1. Em `app/tools.py`:
   - `inspect_directory`: se `directory_path` for vazio ou somente espaços em branco, retornar imediatamente dicionário de erro (`status: "error"`, `error: "INVALID_DIRECTORY"`, `message: "O caminho do diretório não pode ser vazio."`) em vez de listar o diretório atual (`.`).
   - `generate_unified_patch`: normalizar quebras de linha (`\r\n` -> `\n`) tanto no conteúdo lido quanto nos snippets (`original_snippet`, `replacement_snippet`) para compatibilidade perfeita com arquivos Windows CRLF.
   - Em `_count_decisions`: tratar tanto nós Python 3.10+ de pattern matching (`ast.Match` / `ast.match_case` se disponível na versão) de forma resiliente.
2. Em `tests/unit/test_adversarial_tools.py`:
   - Corrigir imports não utilizados para zerar linter ruff (remover F401, I001).
   - Ajustar as asserções para que todos os testes adversariais passem sem erros.

PARTE 2 — IMPLEMENTAÇÃO DO MARCO 2 (M2: Security Guardrails & Interceptors - R2):
1. Implementar `app/guardrails.py`:
   - **Boundary Guard**: `validate_path_boundary(target_path: str, allowed_root: str | None = None) -> tuple[bool, str]`. Normalizar caminhos com `Path(p).resolve().as_posix().lower()` para evitar bypass no Windows. Bloquear path traversal (`..` escapando da raiz) e arquivos protegidos (`.env`, `credentials.json`, `id_rsa*`).
   - **Destructive Command Blocker**: `is_destructive_command(command_line: str) -> tuple[bool, str]`. Regex determinística de alta performance para comandos como `rm -rf`, `Remove-Item -Recurse`, `del /s`, `git reset --hard`, `git clean -fdx`, `git push --force`, `git branch -D`, `DROP DATABASE/TABLE`, `TRUNCATE TABLE`, `format [a-z]:`. Retorna se é destrutivo e motivo explicativo.
   - **Credential & PII Redactor**: `redact_sensitive_info(text: str) -> str`. Sanitização de Google API Keys (`AIza...` -> `[API_KEY_REDACTED]`), Bearer tokens (`Bearer [TOKEN_REDACTED]`), Private Keys (`[PRIVATE_KEY_REDACTED]`), CPF (`[CPF_MASCARADO]`), emails (`[EMAIL_MASCARADO]`).
   - **ADK Lifecycle Interceptors**:
     - `before_tool_guard_callback(tool, args, tool_context) -> dict | None`: inspeciona argumentos de qualquer ferramenta (`file_path`, `directory_path`, `command`). Se detectar violação de fronteira ou comando destrutivo, bloqueia retornando dicionário com status `BLOCKED_BY_GUARDRAIL` e explicação clara (sem executar a ferramenta).
     - `after_tool_sanitizer_callback(tool, args, tool_context, tool_response) -> dict`: varre a resposta da ferramenta e aplica redação em qualquer credencial ou PII antes de retornar ao modelo.
   - **HITL Policy**:
     - `evaluate_hitl_action(action_type: str, details: dict) -> dict`: classifica ações em 3 níveis (Nível 1 - Automático; Nível 2 - Mutação Confinada com Auditoria; Nível 3 - Alto Risco exigindo confirmação explícita).
2. Atualizar `app/__init__.py` para exportar os símbolos de `guardrails.py`.
3. Criar `tests/unit/test_guardrails.py`:
   - Cobertura completa:
     - Boundary Guard com caminhos normais, relativos, tentativas de path traversal fora do workspace (`../../../Windows`), arquivos `.env`.
     - Bloqueio de comandos destrutivos (PowerShell, CMD, Bash, Git, SQL).
     - Mascaramento de chaves AIza, tokens Bearer, senhas e CPFs.
     - Callbacks do ADK `before_tool_guard_callback` bloqueando chamadas inseguras e `after_tool_sanitizer_callback` redigindo retornos.
     - Matriz HITL.

PARTE 3 — VERIFICAÇÃO OBRIGATÓRIA:
Executar no PowerShell e garantir 100% de sucesso:
- `uv run ruff check projects/code_intelligence_agent` -> DEVE RETORNAR 0 ERROS!
- `uv run pytest projects/code_intelligence_agent/tests/unit/ -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"` -> TODOS OS TESTES DEVEM PASSAR!

Ao concluir:
- Escreva seu relatório de handoff em:
  `c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_worker_m2\handoff.md`
- Atualize `progress.md` em sua pasta.
- Envie uma mensagem ao orquestrador relatando os arquivos alterados/criados e os resultados dos comandos de verificação.
