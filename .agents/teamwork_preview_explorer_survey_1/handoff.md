# Relatório de Investigação e Mapeamento de Arquitetura — Explorer 1

**Agente:** Explorer 1 (Mapeamento de Escopo, ADK e Antigravity SDK)  
**Data/Hora:** 2026-09-11T07:12:00Z  
**Diretório de Trabalho:** `c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_explorer_survey_1`  
**Escopo:** Mapeamento de requisitos, arquitetura do Google ADK, Google Antigravity SDK, empacotamento com `uv`, integração FastAPI/CLI e Quality Flywheel para o `projects/code_intelligence_agent`.

---

## 1. Observation (Observações Diretas)

1. **Especificação Original (`ORIGINAL_REQUEST.md`):**
   - No arquivo `c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md` (linhas 44 a 78, seção `## 2026-09-11T07:05:21Z`), constam os requisitos formais para a criação de `projects/code_intelligence_agent`:
     - **R1. Agente de Engenharia e Inteligência de Código:** Inspeção de repositórios, identificação de anomalias sintáticas/estruturais, proposição de correções/patches determinísticos e gestão de estado/raciocínio.
     - **R2. Guardrails e Políticas de Segurança (HITL & Sanitização):** Interceptadores de ciclo de vida (hooks/callbacks) para bloquear comandos destrutivos no SO, mascarar tokens/credenciais sensíveis e proteger fronteiras de diretórios (*directory boundary traversal*).
     - **R3. Suíte de Avaliação Automatizada (Quality Flywheel):** Dataset canônico em `tests/eval/datasets/` para cenários multi-turn e `eval_config.yaml` parametrizando métricas com metas: `multi_turn_task_success >= 0.85` e `multi_turn_tool_use_quality >= 0.80`.
     - **R4. Interface de Execução e Gerenciamento de Ambiente:** Configuração isolada com `uv` (`pyproject.toml`), compatibilidade com FastAPI / ADK API Server e interface de linha de comando CLI.
     - **Critérios de Aceite:** 100% de aprovação em `uv run pytest`, zero erros em `uv run ruff check`, execução de `agents-cli eval run` batendo metas e geração comprovada de relatórios `results_*.json` e `.html`.

2. **Estado Atual do Filesystem (`projects/`):**
   - Inspeção via `list_dir` em `c:\Users\melki\meu-workspace-global\projects` confirmou a presença exclusiva de `web_visual_auditor`. O diretório `projects/code_intelligence_agent` **não existe ainda**.
   - Busca via `find_by_name` por `*code_intelligence*` em todo o workspace retornou 0 resultados.

3. **Ambiente de Runtime e Pacotes Instalados:**
   - Python: `3.12.10` (64-bit AMD64).
   - Gerenciador canônico: `uv` (executando comandos e gerindo `.venv`).
   - `google.adk`: Versão **`2.9.0`** instalada em `C:\Users\melki\meu-workspace-global\.venv\Lib\site-packages\google\adk`.
     - Submódulos confirmados: `agents`, `apps`, `artifacts`, `auth`, `cli`, `code_executors`, `evaluation`, `events`, `memory`, `models`, `plugins`, `runners`, `sessions`, `tools`, `workflow`.
   - `google.antigravity`: Pacote instalado em `C:\Users\melki\meu-workspace-global\.venv\Lib\site-packages\google\antigravity`.
     - Submódulos confirmados: `agent`, `connections`, `hooks`, `policy`, `types`.
   - `agents-cli`: Versão **`1.5.0`** disponível globalmente via PATH em `C:\Users\melki\AppData\Roaming\uv\tools\google-agents-cli`.
     - Comandos confirmados: `create`, `eval` (`run`, `generate`, `grade`, `compare`), `info`, `playground`, `run`, `scaffold`.
   - `google.genai`, `fastapi` e `pydantic` instalados e prontos.

4. **Assinaturas Críticas Inspecionadas no ADK 2.9.0:**
   - `google.adk.cli.fast_api.get_fast_api_app`:
     ```python
     get_fast_api_app(*, agents_dir: str, agent_loader = None, session_service_uri = None, web: bool, port: int = 8000, trigger_sources = None, ...) -> FastAPI
     ```
   - O servidor nativo monta as rotas canônicas `/apps/{app}/users/{user}/sessions/{session}/run` e `/run_sse`.

5. **Regras Canônicas de Convenção ADK Extraídas das Skills:**
   - *Regra do Nome do App (`references/adk-python.md:681`):* O parâmetro `App(name=...)` **deve** ser idêntico ao nome do diretório do agente (ex: se o código reside em `app/`, `App(name="app", root_agent=root_agent)`). Uma discrepância causa falha `Session not found` no runner de avaliação.
   - *Regra de Ferramentas FunctionTool (`references/adk-python.md:363`):* Todas as ferramentas devem possuir type hints estritos, **NÃO devem conter valores default** nos parâmetros da função, docstrings claras explicativas (enviadas ao LLM) e devem retornar dicionários serializáveis em JSON (`dict`).
   - *Regra de Callbacks (`references/adk-python.md:704`):* Callbacks utilizam passagem por keyword arguments onde os nomes dos parâmetros devem bater exatamente (`callback_context`, `llm_request`, `tool`, `args`, `tool_context`, `tool_response`).
   - *Regra de Avaliação Multi-Turn (`references/dataset_schema.md:98`):* Casos de teste multi-turn devem utilizar `agent_data` com lista ordenada de `turns` (turn_index sequencial 0-based), eventos com `author` (`user`, `agent_id`, `tool`), e nunca misturar `prompt` com `agent_data` no mesmo caso.

---

## 2. Logic Chain (Cadeia de Raciocínio)

1. **Necessidade de Modularidade e Isolamento (R1 e R4):**
   - O `ORIGINAL_REQUEST.md` exige que o sistema opere como um pacote autônomo em `projects/code_intelligence_agent`.
   - Para atender ao padrão ADK 2.9.0 e permitir tanto execução via CLI local, servidor FastAPI, quanto avaliação via `agents-cli eval run`, o layout padrão recomendado é:
     - Raiz do projeto: `projects/code_intelligence_agent/`
     - Código do agente: `app/` (permitindo `App(name="app", root_agent=root_agent)`)
     - Ferramentas: `app/tools.py`
     - Políticas de segurança e guardrails: `app/guardrails.py`
     - Servidor FastAPI: `app/fast_api_app.py`
     - Linha de comando: `app/cli.py`
     - Testes e avaliação: `tests/unit/`, `tests/integration/`, `tests/eval/`

2. **Orquestração e Capacidades de Inteligência de Código (R1):**
   - O agente necessita de 4 capacidades instrumentadas via ferramentas funcionais determinísticas:
     1. `inspect_directory(directory_path: str, max_depth: int)`: Mapeamento de estrutura de diretórios e arquivos.
     2. `read_code_file(file_path: str, start_line: int, end_line: int)`: Leitura paginada de código-fonte.
     3. `analyze_ast_anomalies(file_path: str)`: Análise estática com o módulo `ast` do Python 3.12, detectando:
        - Erros de sintaxe (`SyntaxError`).
        - Cláusulas de exceção perigosas (ex: `except:` nu ou `except Exception:` sem supressão).
        - Uso de funções perigosas (`eval()`, `exec()`, `__import__`).
        - Complexidade ciclomática e funções excessivamente longas (>80 linhas).
     4. `generate_unified_patch(file_path: str, original_snippet: str, replacement_snippet: str)`: Geração e validação de patches no formato standard unified diff (`difflib`), garantindo que o patch seja determinístico antes de qualquer modificação.
   - Estado conversacional: Rastreamento em `tool_context.state` (ex: `state["inspected_files"]`, `state["detected_anomalies"]`, `state["active_patches"]`).
   - Modelo: `gemini-3.8-flash` configurado com `generate_content_config=types.GenerateContentConfig(temperature=0.1)` para garantir determinismo nas chamadas de ferramentas.

3. **Arquitetura de Guardrails em Múltiplas Camadas (R2):**
   - A segurança do agente precisa de redundância *Defense-in-Depth*:
     - **Camada 1 — Verificação de Fronteira (Path Traversal Guard):** No hook `before_tool_callback`, inspecionar qualquer parâmetro de caminho (`file_path`, `directory_path`). Resolver o path absoluto via `os.path.realpath` e validar se está contido no workspace autorizado (`os.path.commonpath([resolved, workspace]) == workspace`). Se houver tentativa de fuga (`../../windows/system32`), a execução é abortada retornando um dicionário de violação de segurança antes de atingir o disco.
     - **Camada 2 — Bloqueio de Comandos Destrutivos:** Validação de comandos de terminal ou deleção de arquivos. Comandos como `rm -rf`, `format`, `mkfs`, `git reset --hard`, `DROP TABLE`, `del /s` são interceptados com feedback explicativo.
     - **Camada 3 — Human-in-the-Loop (HITL):** Ações de modificação física de arquivos (`apply_patch`) devem utilizar confirmação humana explícita (`FunctionTool(apply_patch, require_confirmation=True)` ou verificação de flag de autorização em `tool_context.state`).
     - **Camada 4 — Sanitização de Credenciais e PII:** No hook `after_tool_callback`, expressões regulares varrem retornos de ferramentas para mascarar chaves de API (`AIza[0-9A-Za-z-_]{35}`), tokens Bearer (`sk-[a-zA-Z0-9]{32,}`) e senhas, substituindo por `[REDACTED_SECRET]`.

4. **Metodologia de Avaliação e Quality Flywheel (R3):**
   - `agents-cli eval run` espera a seguinte infraestrutura:
     - Arquivo `tests/eval/eval_config.yaml`:
       ```yaml
       metrics_to_run:
         - multi_turn_task_success
         - multi_turn_tool_use_quality
         - multi_turn_trajectory_quality
       ```
     - Dataset `tests/eval/datasets/code_intelligence_eval.json`:
       - Casos multi-turn formatados rigorosamente conforme a especificação do Agent Platform:
         1. *Caso 1: Análise AST e Diagnóstico de Anomalias* (o usuário solicita análise de arquivo com antipadrões; o agente invoca `analyze_ast_anomalies` e resume os problemas).
         2. *Caso 2: Localização de Bug e Geração de Patch* (o usuário aponta um bug lógico; o agente lê o código via `read_code_file`, analisa o erro e propõe patch com `generate_unified_patch`).
         3. *Caso 3: Interceptação de Violação de Diretório / Guardrail* (o usuário tenta fazer o agente ler arquivo fora do workspace; o agente intercepta via guardrail e recusa graciosamente sem falhar).
     - O comando `agents-cli eval run` executa a inferência e o grading via LLM-judge, registrando os relatórios `results_*.json` e `results_*.html` em `artifacts/grade_results/`.

5. **Empacotamento Moderno e Integração FastAPI/CLI (R4):**
   - Empacotamento `uv`: `pyproject.toml` usando `hatchling` com dependências estritas:
     - `google-adk>=2.9.0`
     - `google-antigravity`
     - `google-genai>=2.3.0`
     - `fastapi>=0.115.0`
     - `uvicorn>=0.30.0`
     - `pydantic>=2.8.0`
     - `typer>=0.12.0` (ou `click`/`argparse`)
   - Script de entrada registrado no `[project.scripts]`:
     ```toml
     [project.scripts]
     code-intel = "app.cli:main"
     ```
   - FastAPI: Arquivo `app/fast_api_app.py` integrando `get_fast_api_app(agents_dir=..., web=False)` e adicionando endpoints REST complementares:
     - `GET /healthz`: verificação de integridade e readiness probe.
     - `POST /api/v1/analyze`: invocação direta de análise estática sem streaming.
     - `POST /api/v1/query`: pipeline interativo via `Runner`.
   - CLI: Arquivo `app/cli.py` fornecendo comandos:
     - `code-intel run "<prompt>"`
     - `code-intel inspect <caminho>`
     - `code-intel serve --port 8000`
     - `code-intel eval`

---

## 3. Caveats (Ressalvas e Limitações)

1. **Credenciais de Execução do LLM:**
   - O ADK e o Antigravity SDK necessitam de `GEMINI_API_KEY` (para Google AI Studio) ou credenciais de Application Default Credentials (`gcloud auth application-default login` com `GOOGLE_GENAI_USE_VERTEXAI=true`). Para testes unitários determinísticos, todas as ferramentas e guardrails devem ser testados isoladamente via mocks/fixtures locais sem chamadas remotas de rede.
2. **Ambiente Windows e Pytest:**
   - Conforme documentado em `AGENTS.md`, no Windows o pytest deve sempre receber `--basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"` para evitar o erro de sistema `WinError 5` durante a remoção de symlinks no teardown.
3. **Restrição de Agente Somente Leitura:**
   - Na condição de Explorer 1, nenhuma alteração de código ou criação de pasta de produção foi executada fora de `.agents/teamwork_preview_explorer_survey_1`. O plano detalhado acima está pronto para ser implementado pelo arquiteto / implementador de código.

---

## 4. Conclusion (Conclusão e Proposta de Arquitetura)

O ambiente do workspace já possui todas as dependências críticas instaladas e compatíveis (`google.adk 2.9.0`, `google.antigravity`, `agents-cli 1.5.0`, Python 3.12.10 sob `uv`).

A estrutura proposta para o `projects/code_intelligence_agent` deve ser organizada da seguinte forma:

```
projects/code_intelligence_agent/
├── pyproject.toml                     # Configuração de empacotamento uv e hatchling
├── README.md                          # Documentação operacional e exemplos de uso
├── .env.example                       # Template de variáveis de ambiente
├── app/                               # Pacote canônico do agente ADK
│   ├── __init__.py
│   ├── agent.py                       # Definição de root_agent, App e runner ADK
│   ├── tools.py                       # 4 ferramentas (inspect, read, ast, patch)
│   ├── guardrails.py                  # Interceptadores before/after_tool_callback e sanitização
│   ├── fast_api_app.py                # Wrapper FastAPI compatível com ADK API Server
│   └── cli.py                         # Interface CLI via Typer/Argparse (entrypoint code-intel)
├── tests/
│   ├── conftest.py                    # Fixtures e workspaces temporários isolados
│   ├── unit/
│   │   ├── test_tools.py              # Testes unitários das ferramentas de código
│   │   ├── test_guardrails.py         # Testes de bloqueio de traversal, sanitização e comandos
│   │   ├── test_ast_analyzer.py       # Testes da análise estática AST
│   │   └── test_cli.py                # Testes da interface de linha de comando
│   ├── integration/
│   │   ├── test_fastapi_endpoints.py  # Testes dos endpoints HTTP /healthz e /api/v1
│   │   └── test_agent_runner.py       # Testes do loop de execução via Runner
│   └── eval/
│       ├── eval_config.yaml           # Configuração de métricas do Quality Flywheel
│       └── datasets/
│           └── code_intelligence_eval.json  # Dataset multi-turn com os 3 cenários canônicos
```

### Especificação dos Arquivos Principais:

#### A. `pyproject.toml`
```toml
[project]
name = "code-intelligence-agent"
version = "0.1.0"
description = "Autonomous Code Intelligence & Engineering Agent using Google ADK and Antigravity SDK"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "google-adk>=2.9.0",
    "google-antigravity",
    "google-genai>=2.3.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.8.0",
    "typer>=0.12.0",
]

[project.scripts]
code-intel = "app.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

#### B. `app/guardrails.py` (Resumo Técnico)
- **`SecurityGuardrail`**:
  - `validate_path_boundary(target_path, workspace_root) -> bool`
  - `is_destructive_command(command_str) -> bool`
  - `sanitize_sensitive_data(payload: dict | str) -> dict | str`
  - Callback hook:
    ```python
    async def before_tool_callback(tool, args, tool_context) -> dict | None:
        # 1. Valida boundary se houver path
        # 2. Valida comando se for execução
        # 3. Retorna dict de bloqueio se violado, ou None para autorizar
    ```
    ```python
    async def after_tool_callback(tool, args, tool_context, tool_response) -> dict | None:
        # Sanitiza credenciais e tokens da resposta
        return sanitize_output(tool_response)
    ```

#### C. `app/agent.py` (Resumo Técnico)
```python
from google.adk.agents import Agent
from google.adk.apps import App
from app.tools import inspect_directory, read_code_file, analyze_ast_anomalies, generate_unified_patch
from app.guardrails import before_tool_callback, after_tool_callback

root_agent = Agent(
    name="code_intelligence_agent",
    model="gemini-3.8-flash",
    description="Agente autônomo especialista em inspeção de repositórios, análise estática AST e refatoração segura de código.",
    instruction="""Você é um engenheiro de software e especialista em inteligência de código.
Sua missão é inspecionar diretórios, ler arquivos de código com precisão, identificar anomalias estruturais via AST
e propor correções através de patches unified diff determinísticos.
Nunca execute comandos destrutivos. Respeite estritamente as fronteiras do repositório.""",
    tools=[inspect_directory, read_code_file, analyze_ast_anomalies, generate_unified_patch],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)

app = App(name="app", root_agent=root_agent)
```

---

## 5. Verification Method (Método de Verificação Independente)

Para auditar e verificar as observações deste relatório, execute os seguintes comandos no terminal:

1. **Verificação de Pacotes e Versões do Runtime:**
   ```powershell
   uv run python -c "import google.adk, google.antigravity, google.genai, fastapi; print('ADK:', google.adk.__version__); print('Antigravity: OK'); print('FastAPI:', fastapi.__version__)"
   ```

2. **Verificação do CLI de Agentes:**
   ```powershell
   agents-cli --version
   agents-cli eval --help
   ```

3. **Validação da Assinatura de `get_fast_api_app`:**
   ```powershell
   uv run python -c "from google.adk.cli.fast_api import get_fast_api_app; import inspect; print(inspect.signature(get_fast_api_app))"
   ```

4. **Verificação de Ausência Prévia do Projeto-Alvo:**
   ```powershell
   Get-ChildItem -Path "c:\Users\melki\meu-workspace-global\projects"
   ```

5. **Condição de Invalidação:**
   - Este relatório seria invalidado se o `google.adk` requisesse versão legada incompatível com o Python 3.12, ou se o comando `agents-cli` não estivesse presente no PATH. Ambas as hipóteses foram refutadas por observação direta.
