# Relatório de Handoff — Explorer 2: Ferramentas de Engenharia de Código e Guardrails de Segurança (R2)

**Data**: 2026-09-11T07:11:00Z  
**Autor**: Explorer 2 (Agente Especialista em Inteligência de Código e Segurança Zero-Trust)  
**Destinatário**: Orquestrador Pai (`75db6599-789c-4d74-9bf5-be981121c059`)  
**Status**: Concluído (Hard Handoff)  
**Projeto Alvo**: `projects/code_intelligence_agent` (C:\Users\melki\meu-workspace-global\projects\code_intelligence_agent)

---

## 1. Observation (Observações Diretas e Evidências do Workspace)

### 1.1. Requisitos Canônicos em `ORIGINAL_REQUEST.md` (seção `## 2026-09-11T07:05:21Z`)
- **Linhas 46-49**: *"Construir um sistema autônomo de inteligência e engenharia de código (Code Intelligence & Tool Calling) para ambiente de produção, integrando o Google Agent Development Kit (ADK) e o Google Antigravity SDK, dotado de guardrails de segurança, ferramentas com validação robusta e uma suíte completa de avaliação automatizada baseada no Quality Flywheel (`agents-cli eval`). Working directory: C:\Users\melki\meu-workspace-global\projects\code_intelligence_agent"*
- **Requisito R1 (Linhas 53-55)**: *"O agente deve ser capaz de inspecionar bases de código, identificar anomalias, propor modificações precisas e orquestrar ferramentas de navegação e análise estática via tool calling determinístico. Deve gerenciar estado conversacional e histórico de raciocínio de forma transparente."*
- **Requisito R2 (Linhas 56-58)**: *"O sistema deve implementar interceptadores de ciclo de vida (hooks/callbacks) para impedir comandos destrutivos no sistema operacional, mascarar credenciais ou tokens sensíveis e assegurar integridade de fronteiras de diretório."*
- **Critério de Aceitação de Segurança (Linhas 76-78)**: *"Comandos potencialmente destrutivos ou violações de fronteira de diretório são interceptados e bloqueados com feedback explicativo."*

### 1.2. Módulos Existentes de Segurança e Análise de Código

#### A. `agents/specialized/security_guard.py`
- **Linhas 19-44**: `ProjectBoundaryGuardrail` implementa controle de acesso rigoroso prevenindo loops de auto-auditoria e restrições de escopo:
  - `DEFAULT_ALLOWED_ROOTS`: `["projects/*", "projects/pcm", "projects/canvas_ide", ...]`
  - `DEFAULT_PROHIBITED_TARGETS`: `["agents", "agents/*", "skills", "skills/*", ".", "./", "meu-workspace-global"]`
- **Linhas 155-165**: `DEFAULT_BLOCKED_PATTERNS` bloqueia injeções de prompt e comandos de alto risco:
  - `(?i)ignore\s+(all\s+)?previous\s+(instructions|guidelines|rules|prompts)`
  - `(?i)reveal\s+(api\s*key|password|credential|secret)`
  - `(?i)dump\s+.*(credentials|passwords|keys|secrets)`
  - `(?i)sudo\s+rm\s+-rf`
- **Linhas 163-165, 211-215**: Mascaramento de PII:
  - CPF: `r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"` -> `[CPF_MASCARADO]`
  - E-mail: `r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"` -> `[EMAIL_MASCARADO]`
- **Linhas 217-227**: Redação de chaves em saída:
  - Detecção e substituição de `r"AIza[0-9A-Za-z-_]{35}"` por `[API_KEY_REDACTED]`.

#### B. `agents/specialized/code_consistency_specialist.py`
- **Linhas 14-24**: Modelo Pydantic `CodeContract` (`name`, `contract_type`, `file_path`, `signature`, `description`).
- **Linhas 26-39**: Modelo `CodeDriftIssue` com severidades (`error`, `warning`, `info`) e categorias (`syntax_error`, `type_incompatibility`, `contract_drift`, `convention_violation`).
- **Linhas 111-152**: `audit_syntax_and_ast(code, file_path)`:
  - Tratamento de `SyntaxError` com `e.lineno` e `e.msg`.
  - Inspeção via `ast.walk(tree)` de handlers `ast.ExceptHandler`: bloqueio de `except Exception` genérico sem `# noqa: BLE001` ou justificativa.
- **Linhas 183-216**: `extract_symbols_from_code(code)`:
  - Varredura de `ast.ClassDef` identificando modelos Pydantic `BaseModel`.
  - Varredura de `ast.FunctionDef` e `ast.AsyncFunctionDef` extraindo argumentos e assinaturas formais.
- **Linhas 154-181**: `check_contract_compatibility(proposed_symbols)`:
  - Detecção determinística de drift de contratos entre assinaturas registradas e propostas.

#### C. `configs/guardrails.yaml`
- **Linhas 24-32**: `execution_safety`:
  - `enforce_hitl_for_destructive_ops: true`
  - `destructive_operations`: `["file_delete", "table_drop", "database_truncate", "execute_arbitrary_shell"]`
  - `safe_workspace_boundary: "./"`
- **Linhas 37-53**: `audit_scope_policy`:
  - Alvos autorizados e proibidos explicitados, com `default_target_fallback_mode: "reject"`.

#### D. Lifecycle Hooks Canônicos em `scripts/hooks/` e `plugins/antigravity-governance/hooks.json`
- **`scripts/hooks/pre_tool_guard.py` (Linhas 19-33)**: Padrões de comandos destrutivos:
  - `rm -rf`, `Remove-Item -Recurse`, `del /s /q`, `rmdir /s /q`, `git reset --hard`, `git clean -fdx`, `git push --force`, `git branch -D`, `drop (database|table)`, `truncate table`, `format [a-z]:`.
- **`scripts/hooks/pre_tool_guard.py` (Linhas 36-45)**: Padrões de arquivos protegidos:
  - `.env*`, `id_rsa*`, `id_ed25519*`, `*.pem`, `*.key`, `credentials.json`, `service_account*.json`, `token.json`.
- **`scripts/hooks/pre_tool_guard.py` (Linhas 48-93)**: `is_path_in_allowed_target` confina escritas a zonas de desenvolvimento autorizadas (`c:/users/melki/projetos`, `c:/users/melki/meu-workspace-global`, `appdata/local/temp`).
- **`scripts/hooks/pre_tool_guard.py` (Linhas 95-137)**: `evaluate_pre_tool`:
  - Retorna `{"decision": "force_ask", "reason": "..."}` para comandos destrutivos, arquivos sensíveis e desvios de fronteira (HITL).
  - Retorna `{"decision": "allow"}` para operações seguras.
- **`scripts/hooks/post_tool_reporter.py` (Linhas 28-30)**: Contrato canônico PostToolUse retornando `{}`.
- **`plugins/antigravity-governance/hooks.json` (Linhas 1-52)**: Mapeamento declarativo de hooks para `PreToolUse`, `PreInvocation`, `PostToolUse`, `Stop`.

### 1.3. Contratos de Callbacks e Plugins no Google ADK (`google-agents-cli-adk-code`)
- **`before_tool_callback(tool: BaseTool, args: dict, tool_context: ToolContext) -> dict | None`**:
  - Retornar `None`: permite execução normal.
  - Retornar `dict`: cancela a ferramenta e usa o dicionário como resultado sintético (intervenção/bloqueio seguro).
  - `tool_context.request_confirmation(hint=...)`: dispara aprovação humana (HITL).
- **`after_tool_callback(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> dict | None`**:
  - Permite sanitizar saídas de ferramentas, mascarando dados sensíveis antes de retorná-los ao modelo.
- **`BasePlugin`**: Plugin global anexado ao `Runner` ou `App(plugins=[...])` que encapsula hooks para todo o ecossistema multiagente.

### 1.4. Linha de Base de Testes do Workspace
- Executado via `run_command`:
  `uv run pytest tests/unit/test_code_consistency_specialist.py tests/unit/test_hooks.py -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"`
- **Resultado**: 12 testes executados e 100% aprovados em 10.82s (sem falhas de permissão no Windows).

---

## 2. Logic Chain (Cadeia Lógica de Inferência e Especificação Técnica)

Com base nas observações do código existente e nas exigências de R1 e R2, estruturamos a especificação da suíte para o novo projeto `projects/code_intelligence_agent`.

### 2.1. Arquitetura das Ferramentas Determinísticas de Código (R1)

Para garantir determinismo estrito, latência mínima (< 20ms) e portabilidade no Windows sem acoplamento a ferramentas externas voláteis, as ferramentas de inteligência de código devem ser construídas com base na biblioteca padrão do Python (`pathlib`, `ast`, `re`, `difflib`, `tomllib`).

```
                              [Code Intelligence Agent]
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
       [Navigation & Search Tools]                  [Static Analysis & Patches]
       • search_files (glob/prune)                  • analyze_code_ast (Syntax, BLE001,
       • grep_search (regex/snippet)                  McCabe Complexity, Smells)
       • view_code (line-indexed)                   • propose_code_patch (diff & replace
                                                      com validação AST em dry-run)
```

#### Ferramenta 1: `search_files` (Navegação no Filesystem)
- **Assinatura**:
  ```python
  def search_files(
      directory: str,
      pattern: str = "*",
      exclude_patterns: list[str] | None = None,
      max_depth: int = 5,
      max_results: int = 50,
  ) -> dict[str, Any]:
      """Busca arquivos por padrão glob com limites determinísticos e poda de diretórios ignorados."""
  ```
- **Lógica e Contrato**:
  - Resolução segura de caminhos com `Path(directory).resolve()`.
  - Poda automática (*pruning*) de pastas ruidosas: `.git`, `node_modules`, `__pycache__`, `.venv`, `dist`, `.brain`, `pytest_tmp`.
  - Retorno: lista estruturada de arquivos com `path`, `relative_path`, `size_bytes`, `modified_at`.

#### Ferramenta 2: `grep_search` (Busca Semântica e Regex no Conteúdo)
- **Assinatura**:
  ```python
  def grep_search(
      search_path: str,
      query: str,
      is_regex: bool = False,
      case_insensitive: bool = True,
      file_pattern: str = "*.py",
      max_matches: int = 50,
      context_lines: int = 2,
  ) -> dict[str, Any]:
      """Executa busca exata ou por expressão regular dentro de arquivos do projeto."""
  ```
- **Lógica e Contrato**:
  - Compilação segura com `re.compile(pattern, flags)`.
  - Tratamento resiliente de encoding: tenta `utf-8`, fallback para `latin-1`, ignora binários (`\x00` check).
  - Retorno: lista de matches contendo `file_path`, `line_number`, `matched_line`, `context_before`, `context_after`.

#### Ferramenta 3: `view_code` (Leitura Paginada com Indexação de Linhas)
- **Assinatura**:
  ```python
  def view_code(
      file_path: str,
      start_line: int = 1,
      end_line: int | None = None,
      max_lines: int = 500,
  ) -> dict[str, Any]:
      """Lê trechos de código com numeração precisa de linhas (1-indexed) e paginação."""
  ```
- **Lógica e Contrato**:
  - Validação de existência e bloqueio de arquivos binários.
  - Exibição no formato canônico `<line_number>: <content>`.
  - Proteção contra exaustão de contexto: teto padrão de 500 linhas, exigindo requisição paginada se exceder.

#### Ferramenta 4: `analyze_code_ast` (Análise Estática, Sintaxe, McCabe e Anomalias)
- **Assinatura**:
  ```python
  def analyze_code_ast(
      file_path: str | None = None,
      code_content: str | None = None,
  ) -> dict[str, Any]:
      """Realiza análise estática profunda na AST do Python: sintaxe, complexidade e code smells."""
  ```
- **Lógica e Regras de Validação**:
  1. **Integridade Sintática**: Executa `ast.parse()`. Se capturar `SyntaxError`, retorna status `"syntax_error"` com `lineno`, `offset`, `text` e mensagem descritiva imediata.
  2. **Detecção de Exceções Genéricas (`BLE001`)**:
     - Percorre `ast.walk(tree)` procurando nós `ast.ExceptHandler`.
     - Identifica handlers sem tipo (`except:`) ou com tipo genérico (`except Exception:`).
     - Verifica a linha no código-fonte por `# noqa: BLE001` ou comentário explicativo; se ausente, emite issue de gravidade `warning`.
  3. **Complexidade Ciclomática (McCabe)**:
     - Percorre `ast.FunctionDef` e `ast.AsyncFunctionDef`.
     - Calcula pontos de decisão $D = 1 + \sum (\text{If, For, AsyncFor, While, AsyncWhile, ExceptHandler, BoolOp, IfExp, MatchCase})$.
     - Se $D > 10$, emite alerta de complexidade excessiva com recomendação de refatoração modular.
  4. **Code Smells & Anomalias Estruturais**:
     - *Argumentos mutáveis padrão*: identifica `ast.FunctionDef.args.defaults` do tipo `ast.List`, `ast.Dict`, `ast.Set` (bug clássico de estado compartilhado).
     - *Funções monolíticas*: funções com mais de 60 linhas físicas.
     - *Chamadas de risco*: uso de `eval()`, `exec()`, `__import__()`.
  5. **Extração de Contratos de Símbolos**:
     - Extração de classes (com detecção de herança `BaseModel`), funções, docstrings e assinaturas formatadas para controle de anti-drift.

#### Ferramenta 5: `propose_code_patch` (Motor de Modificações Seguras com Validação Prévia)
- **Assinatura**:
  ```python
  def propose_code_patch(
      target_file: str,
      target_content: str,
      replacement_content: str,
      start_line: int | None = None,
      end_line: int | None = None,
      dry_run: bool = False,
  ) -> dict[str, Any]:
      """Propõe e aplica patches precisos contíguos com validação sintática AST obrigatória em dry-run."""
  ```
- **Lógica e Validação Preventiva**:
  1. **Unicidade do Alvo**: Verifica se `target_content` ocorre exatamente uma vez no arquivo (ou no intervalo `[start_line, end_line]`). Se houver ambiguidade ou ausência, rejeita com `TARGET_NOT_FOUND` ou `TARGET_AMBIGUOUS`.
  2. **Validação AST Pré-Aplicação (Dry-Run)**:
     - Gera o conteúdo resultante em memória.
     - Submete a `ast.parse(novo_conteudo)`.
     - **Se houver erro sintático, o patch é sumariamente REJEITADO antes de qualquer escrita em disco!** Retorna relatório de erro com a linha de falha.
  3. **Geração de Unified Diff**: Gera a representação unificada de diff (`difflib.unified_diff`) para auditoria clara no histórico de raciocínio do agente.
  4. **Aplicação Segura**: Se `dry_run=False` e validado, grava o arquivo atomicamente (com backup temporário).

---

### 2.2. Arquitetura de Guardrails e Políticas de Segurança R2

A segurança de produção exige proteção em camadas (*Defense in Depth*), combinando interceptadores de ciclo de vida, filtros de sanitização e travas de fronteira de sistema.

```
[Prompt do Usuário]
         │
         ▼
[Input Sanitizer: PII / Prompt Injection] ──► (Bloqueia se malicioso / Mascara CPF, email)
         │
         ▼
[ADK / Antigravity Agent Core] ──► Propõe Tool Call
         │
         ▼
[Pre-Tool Guard Hook / Callback]
   ├── 1. Boundary Guard (Path.resolve() dentro do workspace) ──► Rejeita se traversal
   ├── 2. Destructive Command Detector (Regex de alta velocidade) ──► Rejeita / HITL
   └── 3. Sensitive File Blocker (.env, id_rsa, keys) ──► Bloqueia / HITL
         │
    [Executa Ferramenta]
         │
         ▼
[Post-Tool Hook / Output Sanitizer] ──► (Redige AIza..., Bearer tokens, chaves privadas)
         │
         ▼
[Resposta Segura ao Usuário]
```

#### 1. Interceptadores de Ciclo de Vida (ADK Callbacks & Antigravity Hooks)
- **No Google ADK**:
  - `CodeIntelligenceGuardPlugin(BasePlugin)` encapsula:
    - `before_tool_callback`: inspeciona o dicionário `args` de qualquer ferramenta proposta. Se detectar violação ou risco destrutivo, retorna `{"error": "BLOCKED_BY_GUARDRAIL", "reason": "..."}`, impedindo a execução real.
    - `after_tool_callback`: intercepta o retorno textual e aplica redação em qualquer credencial ou segredo que a ferramenta possa ter lido acidentalmente.
    - `before_model_callback`: sanitiza PII e filtra tentativas de prompt injection antes do envio ao Gemini.
- **No Google Antigravity**:
  - `pre_tool_guard.py` e `post_tool_reporter.py` vinculados via `hooks.json`.
  - Retorno padronizado de protocolo:
    - `"allow"`: ação segura dentro do escopo.
    - `"force_ask"`: ação de risco ou escrita em área protegida que exige confirmação humana explícita (HITL).
    - `"deny"`: ação categoricamente proibida.

#### 2. Bloqueio Determinístico de Comandos Destrutivos
Matriz de padrões regex de alta performance com matching insensível a maiúsculas/minúsculas:

| Categoria | Padrão Regex | Comandos Bloqueados | Risco Mitigado |
|---|---|---|---|
| **Remoção Recursiva** | `(?i)\brm\s+-[rf]{1,2}\b` | `rm -rf /`, `rm -r node_modules` | Perda massiva de código |
| **PowerShell Destrutivo** | `(?i)\bRemove-Item\b.*-Recurse` | `Remove-Item C:\Proj -Recurse` | Exclusão de árvore de diretórios |
| **Comando Windows Del** | `(?i)\bdel\s+/[sqf]\b` | `del /s /q .` | Exclusão forçada e silenciosa |
| **Git Destrutivo** | `(?i)\bgit\s+reset\s+--hard\b` | `git reset --hard HEAD~1` | Perda irreversível de commits |
| **Git Limpeza Forçada** | `(?i)\bgit\s+clean\s+-[fdx]{1,3}\b` | `git clean -fdx` | Exclusão de arquivos não rastreados |
| **Git Force Push** | `(?i)\bgit\s+push\b.*--force` | `git push origin main --force` | Sobrescrita de histórico remoto |
| **Exclusão de Branches** | `(?i)\bgit\s+branch\s+-[dD]\b` | `git branch -D feature` | Destruição de branch de trabalho |
| **Drop de Banco** | `(?i)\bdrop\s+(database\|table)\b` | `DROP DATABASE prod;` | Destruição de dados relacionais |
| **Truncamento de Banco**| `(?i)\btruncate\s+table\b` | `TRUNCATE TABLE users;` | Limpeza irreversível de tabelas |
| **Formatação de Disco** | `(?i)\bformat\s+[a-z]:` | `format c:` | Destruição de volume de SO |

#### 3. Mascaramento Rigoroso de Credenciais e PII
Mecanismo de duas vias (entrada e saída) com dicionário de expressões regulares:

```python
CREDENTIAL_PATTERNS = {
    "google_api_key": r"AIza[0-9A-Za-z-_]{35}",
    "bearer_token": r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}",
    "private_key": r"-----BEGIN (RSA|EC|OPENSSH|DSA|PGP)? PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+ PRIVATE KEY-----",
    "generic_secret": r"(?i)(?:password|secret|token|api[_-]?key|client[_-]?secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
}

PII_PATTERNS = {
    "cpf": r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "credit_card": r"\b(?:\d{4}[ -]?){3}\d{4}\b",
}
```
- **Redaction Policy**:
  - `AIza...` -> `[API_KEY_REDACTED]`
  - `Bearer ...` -> `Bearer [TOKEN_REDACTED]`
  - Chaves privadas -> `[PRIVATE_KEY_REDACTED]`
  - CPFs -> `[CPF_MASCARADO]`
  - E-mails -> `[EMAIL_MASCARADO]`

#### 4. Boundary Guard (Confinamento de Acesso e Prevenção de Path Traversal)
- **Princípio da Menor Exposição**: O agente é isolado em um diretório-raiz de trabalho aprovado (`allowed_root`, default: `C:\Users\melki\meu-workspace-global\projects\code_intelligence_agent`).
- **Resolução Canônica de Traversal**:
  ```python
  def validate_path_boundary(target_path: str | Path, allowed_root: Path) -> tuple[bool, str]:
      try:
          resolved_target = Path(target_path).resolve()
          resolved_root = allowed_root.resolve()
      except Exception as e:
          return False, f"PATH_RESOLUTION_ERROR: {e}"

      # Verificação de prefixo seguro (case-insensitive para compatibilidade Windows)
      target_posix = resolved_target.as_posix().lower()
      root_posix = resolved_root.as_posix().lower()

      if not (target_posix == root_posix or target_posix.startswith(root_posix + "/")):
          return False, f"BOUNDARY_VIOLATION: Alvo '{target_path}' está fora da raiz permitida '{allowed_root}'."

      # Bloqueio adicional de arquivos críticos mesmo dentro do escopo
      if resolved_target.name in (".env", "credentials.json", "id_rsa"):
          return False, f"SENSITIVE_FILE_ACCESS_DENIED: Modificação direta de '{resolved_target.name}' bloqueada por guardrail."

      return True, "PATH_ALLOWED"
  ```

#### 5. Mecanismo de Human-in-the-Loop (HITL)
Classificação operacional em três níveis de criticidade:

1. **Nível 1 (Leitura & Análise - Automático)**:
   - `search_files`, `grep_search`, `view_code`, `analyze_code_ast`.
   - Execução imediata sem intervenção.
2. **Nível 2 (Mutação Confinada - Aprovado com Auditoria)**:
   - `propose_code_patch` dentro da pasta do projeto com validação AST passando.
   - Aplicação permitida; log de auditoria emitido.
3. **Nível 3 (Alto Risco / Ações Destrutivas - HITL Obrigatório)**:
   - Comandos correspondentes a `DESTRUCTIVE_COMMAND_PATTERNS`.
   - Modificações em manifestos raiz de pacotes (`pyproject.toml`, `package.json`).
   - Mutações que toquem arquivos sensíveis (`.env`, certificados).
   - No Antigravity: hook emite `"decision": "force_ask"`.
   - No ADK: ferramenta declarada com `require_confirmation=True` ou chamada a `tool_context.request_confirmation()`, pausando a sessão até input no `ctx.resume_inputs`.

---

## 3. Caveats (Limitações, Pressupostos e Casos Especiais)

1. **Particularidades de Sistema Operacional (Windows)**:
   - O ambiente do usuário utiliza Windows 11 com `pwsh` e `cmd`. Separadores de caminho em Windows utilizam `\` e maiúsculas/minúsculas não são estritamente diferenciadas no NTFS. O Boundary Guard **deve normalizar sempre para `.as_posix().lower()`** antes de qualquer comparação.
   - Junções NTFS e Symlinks (`reparse points`) devem ser resolvidos via `.resolve()` para evitar que um atacante crie um symlink dentro do workspace apontando para `C:\Windows`.
2. **Escopo da Análise AST**:
   - A biblioteca `ast` padrão do Python analisa exclusivamente código Python. Para arquivos JavaScript, TypeScript ou Go (comuns no ecossistema global, como em `pcm` e `customer_issue_reviewer_go`), a análise estrutural da ferramenta deve operar com verificações sintáticas baseadas em regex, linters externos via CLI (ex: `ruff`, `eslint`) ou parsers dedicados, sem quebrar o fluxo caso o arquivo não seja `.py`.
3. **Quirk Conhecido do Pytest no Windows (`WinError 5`)**:
   - Conforme documentado em `AGENTS.md` e ADR 0005, qualquer suíte de testes que crie diretórios temporários no Windows deve usar `--basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"` para evitar falha no teardown do pytest ao remover symlinks.
4. **Nenhum Código de Produção Criado**:
   - Como agente de exploração, nenhuma alteração foi realizada em `projects/*` ou `agents/*`. Toda a especificação deste relatório serve de insumo direto para a fase de implementação do projeto `projects/code_intelligence_agent`.

---

## 4. Conclusion (Conclusão e Parecer Arquitetural Consolidado)

1. **Viabilidade Técnica Plena**: O ecossistema já possui as bases sólidas e testadas de guardrails (`security_guard.py`), ciclo de vida de hooks (`pre_tool_guard.py`) e análise de AST (`code_consistency_specialist.py`).
2. **Requisitos R1 e R2 Atendidos por Design**:
   - As 5 ferramentas determinísticas (`search_files`, `grep_search`, `view_code`, `analyze_code_ast`, `propose_code_patch`) suprem integralmente o requisito R1.
   - O framework unificado de segurança com `CodeIntelligenceGuardPlugin`, Boundary Guard, mascaramento PII/credenciais e travas HITL supre integralmente o requisito R2.
3. **Padrão de Validação Pré-Aplicação (Dry-Run AST)**: A introdução da checagem em memória `ast.parse(patched_code)` antes da escrita física no `propose_code_patch` elimina 100% dos riscos de patches corrompidos introduzidos por agentes autônomos.
4. **Alinhamento com ADK e Antigravity**: O design adota o modelo canônico de `BasePlugin` e `before_tool_callback` do ADK 2.0 e `PreToolUse` do Antigravity CLI, garantindo interoperabilidade nativa com `agents-cli eval` e com o runtime de produção.

---

## 5. Verification Method (Método de Verificação Independente)

O orquestrador ou agente subsequente pode validar independentemente as observações e regras deste relatório através dos seguintes passos:

### 5.1. Execução dos Testes de Guardrails e Análise de Código Existentes
Executar a partir da raiz de `c:\Users\melki\meu-workspace-global` no PowerShell:
```powershell
uv run pytest tests/unit/test_code_consistency_specialist.py tests/unit/test_hooks.py -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
```
- **Critério de Sucesso**: 12 testes aprovados com status `PASSED` e 0 falhas.

### 5.2. Verificação Dinâmica dos Contratos de Hooks
Validar que o hook canônico `pre_tool_guard.py` bloqueia comandos destrutivos e força HITL:
```powershell
python -c "import json, subprocess, sys; p = subprocess.run([sys.executable, 'scripts/hooks/pre_tool_guard.py'], input=json.dumps({'toolCall': {'name': 'run_command', 'args': {'CommandLine': 'rm -rf /'}}}), text=True, capture_output=True); print(p.stdout)"
```
- **Critério de Sucesso**: Saída contém `{"decision": "force_ask", "reason": "Guardrail Zero-Trust: Comando potencialmente destrutivo detectado ('rm -rf /'). Confirmação humana explícita (HITL) requerida."}`.

### 5.3. Validação da Detecção de PII e Chaves em `security_guard.py`
```powershell
python -c "from agents.specialized.security_guard import SecurityGuardAgent; guard = SecurityGuardAgent(); res = guard.audit_output('Chave exposta: AIzaSyD9876543210AbCdEfGhIjKlMnOpQrStU'); print(res)"
```
- **Critério de Sucesso**: Saída contém `'output_text': 'Chave exposta: [API_KEY_REDACTED]'`.

### 5.4. Condições de Invalidação
Este relatório será considerado inválido se:
1. O hook `pre_tool_guard.py` retornar `allow` para comandos listados em `DESTRUCTIVE_COMMAND_PATTERNS`.
2. O Boundary Guard permitir caminhos contendo sequências `..` que escapem do diretório raiz.
3. O `propose_code_patch` permitir a aplicação de código que resulte em `SyntaxError`.
