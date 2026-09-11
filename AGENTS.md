# AGENTS.md — meu-workspace-global

Idioma oficial: **Português (BR)** — código, documentação, commits e respostas.

## 1. O que este repositório é

Workspace de ferramentas para **trabalhar em outros projetos** — ele não é, ele mesmo, o projeto-alvo.
- **Regra de ouro**: NUNCA auditar ou "melhorar" este próprio repositório quando o pedido for sobre um projeto em `projects/*`.
- O código real dos clientes vive fora daqui, em `C:\Users\melki\Projetos\`; as pastas em `projects/` são symlinks/junctions (exceto `projects/web_visual_auditor`, que é um pacote Python interno).
- Resolução programática de alvos: `agents/project_resolver.py` (`ProjectTargetResolver.resolve_target(texto)`).

| Projeto | Caminho Canônico | Symlink / Local | Tech Stack | Dev Server / Execução |
|---|---|---|---|---|
| PresCMed (PCM) | `C:\Users\melki\Projetos\pcm` | `projects/pcm` | React 18, Vite, TS, Tailwind, IndexedDB | `npm run dev` (porta 3000) |
| Canvas IDE | `C:\Users\melki\Projetos\canvas_ide` | `projects/canvas_ide` | React, Vite, TS, Tailwind, Canvas API | `npm run dev` (porta 5173 ou `canvas_preview.html`) |
| KeepDocs Workspace | `C:\Users\melki\Projetos\keepdocs-workspace` | `projects/keepdocs-workspace` | React, TS, Streamlit, Python | `npm run dev` (porta 5173) |
| WAOE | `C:\Users\melki\Projetos\WAOE` | `projects/WAOE` | React, TS, Tailwind | `npm run dev` |
| Web Visual Auditor | — (interno) | `projects/web_visual_auditor` | Python 3.11+, Playwright, Pillow, Pydantic | Suíte offline determinística |
| Customer Issue Reviewer | — (interno) | `agents/specialized/customer_issue_reviewer_go` | Go 1.27+, Google ADK v2 | `go run main.go` (porta CLI/Web ADK) |

---

## 2. Comandos de Verificação & Quirks de Ambiente (Windows)

Gerenciador canônico de dependências: **`uv`**.  
`pytest` **não** está no PATH global do Windows. Sempre use `uv run pytest` ou o executável em `.venv\Scripts\pytest.exe`.

### ⚠️ Quirk Crítico do Pytest no Windows (`WinError 5 - Acesso negado`)
O teardown padrão do pytest no Windows tenta remover symlinks em `AppData\Local\Temp\pytest-of-melki\pytest-current` e falha com `PermissionError: [WinError 5]`.
**Sempre forneça `--basetemp` ao rodar pytest**:
```powershell
--basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
```

### Ordem canônica de verificação do workspace:
```powershell
# 1. Linter e conformidade de estilo (Ruff)
uv run ruff check agents tests

# 2. Integridade e validação do catálogo de skills (90+ skills)
uv run python skills/skill_healthcheck.py

# 3. Testes unitários do workspace (46 testes)
uv run pytest tests/unit -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
```

### Execução de testes focados:
- **Arquivo único**:
  ```powershell
  uv run pytest tests/unit/test_project_resolver.py -v --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
  ```
- **Caso de teste específico**:
  ```powershell
  uv run pytest tests/unit/test_project_resolver.py -k "test_target_project_resolver_prioritizes_workspace" -v --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
  ```
- **Testes do Web Visual Auditor** (167 testes determinísticos):
  ```powershell
  uv run pytest projects/web_visual_auditor/tests -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
  ```
- **Testes do Customer Issue Reviewer (Go)**:
  *Atenção:* O pacote Go fica em `agents/specialized/customer_issue_reviewer_go`, **não** em `projects/` (Makefile legado possui caminho desatualizado).
  ```powershell
  cd agents/specialized/customer_issue_reviewer_go; go test ./... -v
  ```

---

## 3. Como o Trabalho Acontece (Sem Orquestrador Python em Background)

O Claude Code e o OpenCode são os motores de execução direta:
- **Skill tool**: lê `.claude/skills/*/SKILL.md` ou `published_skills/` sob demanda. A junction global `~/.claude/skills` aponta para `published_skills/` (gerada por `uv run python scripts/sync_flat_catalog.py` ou `make sync-skills`).
- **Subagentes dedicados**: definidos em `.agents/agents/*.md` (`arquiteto.md`, `code-auditor.md`, `workspace-researcher.md`, `adk-innovations-researcher.md`, `web-researcher.md`) — atuam sob demanda explícita, sem poluir o fluxo diário de código.
- **Nenhum processo Python em background é necessário**: `orchestrator.py`, `dispatcher.py`, `router.py`, `run.ps1`, API Gateway e servidor FastMCP foram removidos (descontinuados em 2026-09-05 por gerarem stubs simulados).

### Subagentes Dedicados Ativos (`.agents/agents/*.md`):
- `arquiteto.md`: Engenheiro de sistemas e arquiteto de conteúdo/soluções (Modos A/B/C/D com auto-reflexão obrigatória).
- `code-auditor.md`: Auditor Zero-Trust focado exclusivamente nos projetos clientes em `projects/*`.
- `workspace-researcher.md`: Pesquisador estrutural local (leitura estrita de código e arquivos).
- `adk-innovations-researcher.md`: Pesquisa técnica de ponta no ecossistema Google ADK, Gemini API e skills.
- `web-researcher.md`: Pesquisa web geral de bibliotecas externas e documentações sem inflar o contexto raiz.

### Padrão de Ferramentas de Subagentes (`CANONICAL_TOOLS`):
- Subagentes em `.agents/agents/*.md` devem declarar estritamente ferramentas canônicas (`search_web`, `read_url_content`, `view_file`, `grep_search`, `find_by_name`, `list_dir`, `run_command`, `write_to_file`, `replace_file_content`, `ask_question`), prevenindo falhas de contrato em `test_custom_agents_healthcheck.py`.

### Memória Operacional de Rotas & TaskOrganizer:
- Registro quantitativo e histórico de aprendizado em `configs/orchestration_routes_memory.json` e guia em `docs/MATRIZ_ROTAS_E_MEMORIA.md`.
- Atualizações de contadores e taxas de sucesso devem ocorrer via buffer assíncrono em `shared/task_organizer.py` (`record_route_execution` -> `flush_memory_updates`), eliminando gargalos de I/O em tempo real.

### Utilitários determinísticos reais que sobreviveram e estão ativos:
- `shared/task_organizer.py`: `TaskOrganizer` — resolução de rotas consagradas e integração em lote com `skill-factory`.
- `agents/project_resolver.py`: `ProjectTargetResolver` — resolução nome casual → caminho canônico + stack detectada.
- `agents/specialized/security_guard.py`: `ProjectBoundaryGuardrail` (bloqueia auto-auditoria indevida) e `SecurityGuardAgent` (sanitização de PII e bloqueio de vazamento de chaves).
- `agents/specialized/workspace_specialist.py`: varredura de filesystem e detecção de stacks (`package.json`, `pyproject.toml`, `go.mod`).
- `agents/specialized/code_consistency_specialist.py`: análise AST real de Python (erros de sintaxe, `except Exception` sem noqa, compatibilidade de contratos).
- `skills/skill_healthcheck.py`: valida frontmatter YAML, nomes e integridade de todo o catálogo.

---

## 4. Convenções, Segurança e Guardrails

- **Zero-Trust & HITL**: Comandos destrutivos (`rm -rf`, `Remove-Item -Recurse`, `git reset --hard`, `git push --force`, `git branch -D`, `DROP/TRUNCATE`) exigem confirmação humana explícita.
- **Mascaramento de PII & Chaves**: CPF, e-mails e API keys (`AIza...`) são mascarados/redigidos automaticamente por `security_guard.py`. Nunca commitar `.env`, `configs/credentials.json` ou tokens.
- **Hub Central Global**: `C:\Users\melki\.gemini` é o centro de controle, configurações e hooks canônicos. Binário oficial do Google Antigravity: `%LOCALAPPDATA%\agy\bin\agy.exe`.
- **Knowledge Base & Grounding**: `C:\Users\melki\Documents\antigravity\wise-galileo` (`INDEX.md` SSoT e pasta `/boost`), ancorado no Caderno do NotebookLM (`974e4f94-1caf-4828-b90e-3da5c499d1e6`).
- **Lifecycle Hooks**: Devem residir em `C:\Users\melki\.gemini\scripts\hooks\` ou `scripts/hooks/` (`pre_tool_guard.py`, `post_tool_reporter.py`, `pre_invocation_reminder.py`, `stop_verifier.py`). Proibido registrar hooks no-op que introduzam spawn desnecessário de subprocessos no Windows.
- **GCP Orchestration & PySpark**: Pipelines seguem modelo de 3 níveis (Python -> Dataproc Serverless PySpark -> BigQuery SQL), com tag `job:datacloud:antigravity` e URIs `gs://` resolvidas pelo driver do Spark (nunca `os.path.exists`).
- **Escopo de Skills**: Skills de governança (`skill-healthcheck`, `skill-factory`) devem ser usadas no contexto deste workspace.

## PresCMed — decisão de 08/09/2026

O único projeto PresCMed em uso é `C:\Users\melki\Projetos\pcm`. As variantes remix-prescmed-new, PresCMed-new e pessoal-med-web foram retiradas por solicitação do usuário, com cópias de recuperação em `_Arquivo/organizacao-20260908`. Não recriar essas variantes ou seus atalhos.
