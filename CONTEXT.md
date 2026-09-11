# Meta-Workspace Global & Ecossistema de Orquestração Cognitiva

Ambiente operacional de engenharia de software governada, inteligência multi-agente e catálogo de habilidades (Skills) do ecossistema de Melki, integrado ao Hub Central Global (`C:\Users\melki\.gemini`) e alinhado à Topologia em 4 Camadas.

---

## 🏛️ Topologia Arquitetural em 4 Camadas

1. **Camada 1 — Grounding Cognitivo (Google NotebookLM)**:
   - Caderno canônico de referência (`974e4f94-1caf-4828-b90e-3da5c499d1e6`), garantindo ancoragem rigorosa (*Strict Groundedness*), síntese cruzada e Audio Overviews.

2. **Camada 2 — Nuvem & Persistência (Google Drive)**:
   - Estrutura hierárquica governada: `01_gd_bancodedados_workspace` (raiz), `01_agentes_e_skills`, `07_appsheets_e_dados`, `08_inbox_e_uploads` e `/boost`.

3. **Camada 3 — Hub Central Global (Estação de Trabalho Local)**:
   - `C:\Users\melki\.gemini`: Fonte Única de Verdade (SSoT) de projetos (`projects.json`), scripts canônicos de Lifecycle Hooks (`pre_tool_guard.py`), configurações de MCP e runtimes do Antigravity CLI.

4. **Camada 4 — Orquestração Local & Workspaces Clientes**:
   - `C:\Users\melki\meu-workspace-global`: Meta-workspace de ferramentas, testes (`uv`), validações e junctions NTFS.
   - `C:\Users\melki\Projetos\*`: Código-fonte de produção das aplicações clientes (`pcm`, `remix-prescmed-new`, `canvas_ide`, `keepdocs-workspace`, `WAOE`, `tactile-ui-studio`).
   - `C:\Users\melki\Documents\antigravity\wise-galileo`: Base de conhecimento Agent-Readable (`INDEX.md` e `/boost`).

---

## 📖 Linguagem Ubíqua

**Meta-Workspace**:
O ambiente e plataforma global de ferramentas e testes (`meu-workspace-global`), isolado via gerenciador `uv`, provendo módulos auxiliares e junctions para operar sobre projetos clientes.
_Avoid_: Monólito, Backend de produção, Ponto de partida global

**Hub Central Global (`.gemini`)**:
Núcleo primário de autoridade do sistema operacional de IAs, residindo em `C:\Users\melki\.gemini`. Hospeda o registro SSoT de projetos (`projects.json`), os manifestos canônicos de hooks e MCPs.
_Avoid_: Pasta secundária, Diretório descartável

**Projeto Alvo (Target Project)**:
Qualquer repositório ou aplicação cliente em `C:\Users\melki\Projetos` sobre a qual agentes operam sob demanda explícita.
_Avoid_: Submódulo embutido, Projeto legado

**SSoT de Projetos (`projects.json`)**:
O arquivo canônico `C:\Users\melki\.gemini\projects.json` que define o mapeamento autoritativo de caminhos e aliases de todos os projetos do ecossistema.
_Avoid_: Dicionários hardcoded dispersos, Listas locais redundantes

**ProjectTargetResolver**:
Deep Module desacoplado (`agents/project_resolver.py`) que consome a SSoT, resolve caminhos determinísticos (Projetos ↔ junctions), efetua normalização de aliases e realiza detecção profunda de stacks tecnológicas (`package.json`, `pyproject.toml`, `go.mod`).
_Avoid_: Parser simples de string, Dicionário estático

**Lifecycle Hooks (Antigravity Seams)**:
Costura canônica de interceptação e auditoria do Antigravity CLI acoplada a eventos determinísticos (`PreToolUse`, `PreInvocation`, `PostToolUse`, `Stop`).
_Avoid_: Middleware HTTP, Gateway SSE, Polling

**Seam de Segurança (`pre_tool_guard.py`)**:
Hook executado sincronicamente no evento `PreToolUse` para impor guardrails Zero-Trust: intercepta comandos destrutivos, mutações em arquivos sensíveis (`.env`, `credentials.json`, `id_rsa`) e escritas fora das fronteiras de desenvolvimento autorizadas, acionando HITL (`force_ask`).
_Avoid_: Interceptador assíncrono, Script pesado com dependências externas

**Human-in-the-Loop (HITL)**:
Mecanismo de salvaguarda onde decisões críticas, destrutivas ou de fronteira exigem autorização humana prévia e explícita antes do disparo da ferramenta.
_Avoid_: Bypass silencioso, Auto-aprovação cega

**Skill**:
Unidade atômica ou bundle governado de conhecimento procedimental com manifesto YAML padronizado (`SKILL.md`), instruções e scripts consumidos progressivamente por agentes.
_Avoid_: Script solto, Plugin genérico

**Subagente Especializado**:
Agente autônomo com foco de domínio estrito e isolado (ex: auditoria de código, infraestrutura E2E, pesquisa de workspace), despachado sob demanda via ADK ou Antigravity CLI.
_Avoid_: Worker genérico não-supervisionado, Thread solta

**Barramento MCP (Tool Bus)**:
Camada padronizada de ferramentas do Model Context Protocol (FastMCP e runtimes nativos Node/Python) conectando os agentes a ferramentas locais e recursos de nuvem (Google Cloud, Firebase, DevTools).
_Avoid_: Client SDK manual, RPC customizado
