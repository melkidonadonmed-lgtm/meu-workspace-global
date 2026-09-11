# ADR 0005: Lifecycle Hooks Canônicos, Antigravity Subagents e SSoT de Projetos

## Status
Aceito (Accepted) — 2026-09-08

## Contexto
Em 2026-09-05, o ecossistema local passou por uma transição arquitetural profunda: o antigo monolito baseado em servidor SSE (porta 8000) e gateway FastMCP (porta 8080) com `MasterOrchestrator` foi descontinuado em favor da integração nativa com o **Google Antigravity CLI (Antigravity 2.0 / AGY)** e execução de subagentes especializados sob o ADK.

Contudo, a auditoria arquitetural realizada em 2026-09-08 identificou três fragilidades residuais:
1. **Dispersão de Metadados de Projetos**: Mapeamentos de projetos e aliases estavam duplicados em múltiplos arquivos (`projects_dashboard.py`, `run-project.ps1`, `project_resolver.py`, `security_guard.py`), divergindo da fonte oficial em `.gemini/projects.json`.
2. **Duplicação de Detecção de Stacks**: Módulos rasos (`WorkspaceSpecialistAgent`) duplicavam a lógica de inspeção de dependências (`package.json`, `pyproject.toml`, `go.mod`) de `project_resolver.py`.
3. **Lacuna na Seam de Segurança**: O hook `pre_tool_guard.py` verificava comandos destrutivos e arquivos sensíveis por nome simples (`Path.name`), mas não impunha restrições de fronteira de diretórios no sistema de arquivos do usuário.

## Decisão

1. **Adotar `C:\Users\melki\.gemini\projects.json` como SSoT Canônica**:
   - Todo mapeamento de projetos clientes, aliases e caminhos físicos deriva do registro oficial.
   - Centralizar a resolução no Deep Module `ProjectTargetResolver` (`agents/project_resolver.py`), com modelos tipados Pydantic/dataclasses e suporte a monorepos (ex.: `tactile-ui-studio` -> `apps/atlas-ui-kit`).

2. **Absorção de Módulos Rasos**:
   - `WorkspaceSpecialistAgent` torna-se um delegador magro que consome `ProjectTargetResolver.scan_directory()`, eliminando duplicações textuais.
   - `projects_dashboard.py` consome diretamente `ProjectTargetResolver.list_all_projects()`.

3. **Endurecimento da Seam de Segurança (`pre_tool_guard.py`)**:
   - O hook canônico reside em `C:\Users\melki\.gemini\scripts\hooks\pre_tool_guard.py` e executa no evento `PreToolUse`.
   - Incorpora validação de fronteiras de diretórios em Python puro (sem dependências externas para manter latência < 15ms no Windows): mutações fora dos projetos autorizados disparam obrigatoriamente confirmação humana (`force_ask` - HITL).
   - Suítes de testes unitários (`test_hooks.py`) executam estritamente contra a seam canônica em `.gemini`.

4. **Estabilidade de Testes no Windows**:
   - Configuração de `tmp_path_retention_count = 0` e injeção de `--basetemp` em `pyproject.toml` para prevenir `PermissionError: [WinError 5]` durante o teardown do pytest no Windows.

## Consequências

### Positivas
- **Integridade Zero-Trust**: Eliminação de escritas acidentais fora do escopo de projetos em desenvolvimento.
- **Alta Coesão e Baixo Acoplamento**: Uma única implementação robusta de resolução e detecção de stacks consumida por agentes, CLI e dashboards.
- **Performance**: Execução limpa e ultrarrápida no Windows sem overhead desnecessário de processos.
- **Conformidade Documental**: `CONTEXT.md` sincronizado com a Topologia em 4 Camadas estabelecida em `AGENTS.md`.

### Mitigações
- Mutações legítimas em áreas governadas (ex.: `.gemini/` ou `skills/`) requerem aprovação explícita HITL no terminal pelo operador humano.
