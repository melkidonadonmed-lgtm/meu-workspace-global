# Relatório de Handoff — Marco 2: Security Guardrails & Interceptors (R2) + Correções de M1

**Marco:** M2 — Security Guardrails & Interceptors (R2) e Correções Pontuais de M1  
**Agente:** Worker 2 (`teamwork_preview_worker_m2`)  
**Papéis:** implementer, qa, specialist  
**Projeto Alvo:** `projects/code_intelligence_agent` (`C:\Users\melki\meu-workspace-global\projects\code_intelligence_agent`)  
**Data/Hora:** 2026-09-11T07:41:00Z  
**Status:** Concluído (Hard Handoff)  
**Veredito:** **APPROVE**  

---

## 1. Observation (Observações Diretas e Evidências Empíricas)

### 1.1. Linha de Base e Correções de M1
1. **`app/tools.py`:**
   - **`inspect_directory` (Linhas 34-46):** Adicionada verificação no início da função `if not directory_path or not directory_path.strip():` retornando imediatamente `status: "error"`, `error: "INVALID_DIRECTORY"` e `message: "O caminho do diretório não pode ser vazio."`, impedindo vazamento acidental do diretório atual de trabalho (`.`).
   - **`_count_decisions` (Linhas 273-277):** Resolução resiliente de nós Python 3.10+ de pattern matching, cobrindo `ast.match_case` e `ast.MatchCase` de forma segura via `getattr(ast, ...)` e `isinstance`, somando corretamente os ramos de decisão na complexidade McCabe sem gerar exceções.
   - **`generate_unified_patch` (Linhas 596-600, 623, 668-672):** Normalização explícita de quebras de linha `\r\n` -> `\n` tanto em `original_content` quanto em `original_snippet` e `replacement_snippet` antes da verificação de contagem e substituição. Gravação atômica enriquecida com UUID (`f"{target_file.name}.tmp_{os.getpid()}_{uuid.uuid4().hex[:8]}"`) para mitigar colisões em execução assíncrona.
2. **`tests/unit/test_adversarial_tools.py`:**
   - Ordenação dos imports conforme PEP 8 e remoção de imports não utilizados.
   - Ajustadas as asserções de `test_no_unhandled_crashes_on_pathological_inputs` para esperar `INVALID_DIRECTORY`.
   - Atualizados os testes `test_vulnerability_crlf_mismatch_in_generate_unified_patch` e `test_vulnerability_match_case_ast_mccabe_silent_omission`, comprovando a aplicação com sucesso de patches em arquivos CRLF e o cálculo exato de complexidade McCabe (complexidade 5) para declarações `match ... case`.

### 1.2. Implementação do Marco 2 (M2: Security Guardrails & Interceptors - R2)
1. **`app/guardrails.py` (Novo arquivo criado com 362 linhas):**
   - **Boundary Guard (`validate_path_boundary`):** Normaliza alvos e raízes via `Path(p).resolve().as_posix().lower()`. Confinamento estrito contra path traversal (`..` escapando do workspace) e bloqueio categorizado de arquivos sensíveis (`.env`, `.env.*`, `credentials.json`, `token.json`, `service_account*.json`, `id_rsa*`, `id_ed25519*`, `*.pem`, `*.key`, `*.pfx`, `*.p12`).
   - **Destructive Command Blocker (`is_destructive_command`):** Regras regex compiladas de alta performance cobrindo comandos perigosos em Linux/macOS (`rm -rf`, `rm -r`), PowerShell (`Remove-Item -Recurse`), CMD Windows (`del /s`, `erase /s`, `rmdir /s`, `rd /s`), Git (`git reset --hard`, `git clean -fdx`, `git push --force`, `git branch -D`), SQL (`DROP DATABASE/TABLE/SCHEMA`, `TRUNCATE TABLE`), formatação de volume (`format [a-z]:`) e gravação em blocos (`dd`).
   - **Credential & PII Redactor (`redact_sensitive_info` e `sanitize_data`):** Sanitização de Google API Keys (`AIza...` com tolerância de 30 a 45 caracteres), Bearer Tokens (`Bearer [TOKEN_REDACTED]`), chaves privadas PEM/OpenSSH (`[PRIVATE_KEY_REDACTED]`), CPFs (`[CPF_MASCARADO]`), e-mails (`[EMAIL_MASCARADO]`) e senhas explícitas em chave=valor (`[SENHA_REDACTED]`). Função `sanitize_data` opera recursivamente sobre dicts, lists, tuples e sets.
   - **ADK Lifecycle Interceptors:**
     - `before_tool_guard_callback(tool, args, tool_context)`: Inspeciona chaves de caminho (`file_path`, `directory_path`, `target_file`, etc.) e comando (`command`, `command_line`, `cmd`, etc.). Bloqueia chamadas inseguras retornando `dict` com `status: "BLOCKED_BY_GUARDRAIL"` e explicação clara sem executar a ferramenta. Retorna `None` para chamadas autorizadas.
     - `after_tool_sanitizer_callback(tool, args, tool_context, tool_response)`: Higieniza o retorno da ferramenta antes de devolvê-lo ao modelo Gemini.
   - **HITL Policy (`evaluate_hitl_action`):** Matriz de classificação em 3 níveis (Nível 1 - Automático para leitura e análise; Nível 2 - Mutação Confinada com Auditoria para patches e criação de código; Nível 3 - Alto Risco para exclusões, comandos de terminal ou violações de fronteira).
2. **`app/agent.py`:**
   - Conexão nativa de `before_tool_callback=before_tool_guard_callback` e `after_tool_callback=combined_after_tool_callback` ao `root_agent = Agent(...)`.
3. **`app/__init__.py`:**
   - Exportação formal de todos os símbolos de guardrails e tools (`validate_path_boundary`, `is_destructive_command`, `redact_sensitive_info`, `sanitize_data`, `before_tool_guard_callback`, `after_tool_sanitizer_callback`, `evaluate_hitl_action`).
4. **`tests/unit/test_guardrails.py` (Novo arquivo com 16 testes automatizados):**
   - Cobertura integral das 5 dimensões de segurança: Boundary Guard, Bloqueio de Comandos, Redação de Credenciais/PII, Callbacks ADK e Matriz HITL.

### 1.3. Evidências Verbatim de Execução
1. **Linter Ruff (`uv run ruff check projects/code_intelligence_agent`):**
   ```
   All checks passed!
   ```
   *Exit code: 0 | Total de violações: 0.*

2. **Suíte Pytest Unitária (`uv run pytest projects/code_intelligence_agent/tests/unit/ -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"`):**
   ```
   ======================== 50 passed, 1 warning in 2.66s ========================
   ```
   *Total de testes: 50 | Aprovados: 50 (100%) | Falhas: 0.*

---

## 2. Logic Chain (Cadeia Lógica de Dedução)

1. **Da Necessidade de Resiliência no Ambiente Windows e Entradas Adversariais:**
   - O Reviewer M1 e o Challenger M1 observaram que strings vazias em `inspect_directory` resolviam para `Path(".")`, expondo a raiz do repositório. A validação `if not directory_path or not directory_path.strip():` bloqueia o vazamento na raiz e padroniza o contrato de erro `INVALID_DIRECTORY`.
   - Arquivos gravados no Windows frequentemente utilizam quebras CRLF (`\r\n`), enquanto ferramentas de leitura normalizam para LF (`\n`). A normalização em `generate_unified_patch` eliminou falsos negativos de `TARGET_NOT_FOUND` sem comprometer a integridade do arquivo em disco.
   - O Python 3.10+ introduziu `ast.match_case` para os ramos do comando `match`. A detecção dinâmica de classes de matching em `_count_decisions` assegura cálculo determinístico da complexidade ciclomática de McCabe.
2. **Do Confinamento Zero-Trust e Prevenção de Path Traversal:**
   - A normalização com `.resolve().as_posix().lower()` garante que tentativas de escapar da raiz autorizada via sequências `..` ou barras inconsistentes sejam detectadas antes de qualquer operação de I/O.
   - O bloqueio específico de arquivos protegidos (`.env`, `credentials.json`, certificados `.pem`/`.key`) impede o exfiltro acidental de segredos operacionais.
3. **Do Bloqueio Determinístico de Comandos e Sanitização de Saída:**
   - Comandos destrutivos de sistema operacional colocam em risco o ambiente de desenvolvimento. O `is_destructive_command` intercepta chamadas de alto risco e fornece feedback explicativo imediato.
   - A redação de credenciais e PII (Google API Keys, Bearer tokens, CPFs e e-mails) atua em duas vias, assegurando que o modelo e o histórico do agente permaneçam protegidos contra vazamentos de conformidade.
4. **Da Interoperabilidade com o Google ADK:**
   - A assinatura dos interceptadores `before_tool_guard_callback` e `after_tool_sanitizer_callback` cumpre rigorosamente o contrato do ADK 2.9.0, permitindo interceptação e cancelamento transparente sem quebrar o ciclo de vida do agente.

---

## 3. Caveats (Ressalvas)

- **Avisos de Depreciação do ADK:** Foi observado 1 warning de depreciação originário internamente da biblioteca `google-adk` (`DeprecationWarning: BaseAgentConfig is deprecated...`). Esse aviso pertence ao código upstream do framework e não afeta a execução ou estabilidade do projeto.
- **Ambiente Windows:** A flag `--basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"` permanece mandatória para evitar `WinError 5 (PermissionError)` durante o teardown de symlinks pelo pytest no Windows.
- **Não Violação de Integridade:** Não foram utilizadas implementações simuladas (stubs), mocks de conveniência no código de produção ou respostas hardcoded. Toda a lógica é genuína e mantém estado real.

---

## 4. Conclusion (Conclusão)

- **Veredito Formal:** **APPROVE**.
- Todas as correções pontuais do Marco 1 foram concluídas e validadas.
- O Marco 2 (M2: Security Guardrails & Interceptors - R2) foi completamente implementado, com todas as regras de segurança Zero-Trust, interceptadores ADK, mascaramento de dados e política HITL operacionais.
- A suíte unitária do projeto saltou de 34 para **50 testes automatizados**, todos executando com 100% de sucesso e linter Ruff com zero violações.
- O projeto `projects/code_intelligence_agent` está pronto para o avanço para o **Marco 3: Interfaces (CLI/FastAPI) & Quality Flywheel (R3)**.

---

## 5. Verification Method (Método de Verificação Independente)

Para auditar e reproduzir empiricamente todas as verificações deste relatório:

1. **Auditoria de Estilo e Conformidade com Ruff:**
   ```powershell
   uv run ruff check projects/code_intelligence_agent
   ```
   *Expectativa:* `All checks passed!` (0 erros).

2. **Execução de Toda a Suíte Unitária (50 testes):**
   ```powershell
   uv run pytest projects/code_intelligence_agent/tests/unit/ -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
   ```
   *Expectativa:* `50 passed, 1 warning in ~2.7s`.

3. **Execução Focada da Suíte de Guardrails de Segurança:**
   ```powershell
   uv run pytest projects/code_intelligence_agent/tests/unit/test_guardrails.py -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
   ```
   *Expectativa:* `16 passed in ~0.3s`.

4. **Execução Focada dos Testes Adversariais de Ferramentas:**
   ```powershell
   uv run pytest projects/code_intelligence_agent/tests/unit/test_adversarial_tools.py -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
   ```
   *Expectativa:* `18 passed in ~0.4s`.
