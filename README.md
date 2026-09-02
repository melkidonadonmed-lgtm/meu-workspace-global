# 🌐 Repositório Global de Agentes Autônomos, Skills & FastMCP

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Model](https://img.shields.io/badge/model-Gemini%203.7%20Flash-orange.svg)](https://ai.google.dev/)
[![Protocol](https://img.shields.io/badge/MCP-FastMCP%20Multi--Transport-green.svg)](https://modelcontextprotocol.io/)
[![Architecture](https://img.shields.io/badge/architecture-Strict%20Separation%20of%20Concerns-purple.svg)](#)

Este repositório consolida a **arquitetura de repositório global ideal** para operar agentes de inteligência artificial de alta performance, catálogo modular de habilidades (`SKILL.md`), servidores de ferramentas do Model Context Protocol (FastMCP) e aplicações web isoladas.

---

## 🏛️ Árvore de Diretórios Global

```text
meu-workspace-global/
├── 📁 .codex/                        # Configuração do Codex no escopo do projeto
│   └── 📄 config.toml                # OpenAI Docs MCP oficial e somente leitura
│
├── 📁 agents/                        # Hub Central de Agentes e Orquestração (Google Antigravity SDK)
│   ├── 📄 __init__.py                # Módulo exportável
│   ├── 📄 orchestrator.py            # Orquestrador Stateful (Gemini Interactions API + Memória)
│   ├── 📄 antigravity_bridge.py      # Ponte oficial com o Google Antigravity SDK (Python)
│   ├── 📄 api_gateway.py             # Servidor de API (FastAPI / SSE Streaming)
│   └── 📁 specialized/              # Subagentes Especialistas Stateless
│       ├── 📄 __init__.py
│       ├── 📄 html_modular_specialist.py # Especialista em páginas HTML5 e Atomic Design
│       ├── 📄 research_evolution_specialist.py # Pesquisa web e evolução do workspace
│       ├── 📄 sql_specialist.py      # Agente especialista em consultas e otimização SQL
│       ├── 📄 workspace_specialist.py# Agente para manipulação de arquivos e sistema
│       └── 📄 security_guard.py      # Guardrail Zero-Trust e validação de segurança/PII
│
├── 📁 skills/                        # Catálogo e Biblioteca Reutilizável de Habilidades
│   ├── 📄 skill_parser.py            # Motor de descoberta e injeção dinâmica (Progressive Disclosure)
│   ├── 📄 README.md                  # Índice e inventário do catálogo de skills
│   ├── 📁 research/                  # Bundle de pesquisa (parent com has-sub-skill)
│   │   ├── 📄 SKILL.md               # Especificação do parent
│   │   ├── 📁 deep-research/         # Sub-skill de pesquisa web multi-fonte
│   │   └── 📁 notebooklm/            # Sub-skill de consulta a cadernos NotebookLM
│   ├── 📁 ui-engineering/            # Bundle de interface (frontend, a11y, html-modular-builder)
│   ├── 📁 auditoria/                 # Bundle de auditoria (code-validator, skill-repo-analyser)
│   └── 📁 skill-prompt-generator/    # Skill standalone
│       └── 📄 SKILL.md
│
├── 📁 mcp_servers/                   # Servidores FastMCP (Model Context Protocol)
│   ├── 📄 server.py                  # Servidor MCP unificado (Multi-Transporte: stdio + SSE)
│   ├── 📄 mcp_config.json            # Manifesto para Antigravity, Cursor e Claude
│   └── 📁 tools/                     # Módulos de ferramentas e conectores de API
│       ├── 📄 google_workspace.py    # Conector Google Drive/Docs/Sheets
│       └── 📄 bigquery_analytics.py  # Conector de análise de dados
│
├── 📁 configs/                       # Configurações, Manifestos e Guardrails
│   ├── 📄 agents_manifest.yaml       # Declaração central de agentes, modelos e permissões
│   ├── 📄 guardrails.yaml            # Regras de segurança, sanitização e OWASP LLM01
│   └── 📄 .env.example               # Template de variáveis de ambiente do ecossistema
│
├── 📁 projects/                      # Aplicações Clientes e Módulos Standalone
│   ├── 📁 canvas_ide/                # Frontend (React + TypeScript + Tailwind)
│   │   ├── 📄 package.json           # Dependências Node.js isoladas
│   │   └── 📄 README.md
│   ├── 📁 customer_issue_reviewer_go/# Agente em Go com Google ADK v2 (Issue Reviewer & SRE Report)
│   │   ├── 📄 go.mod                 # Módulo Go (google.golang.org/adk/v2)
│   │   ├── 📄 main.go                # CLI Launcher e Web UI ADK
│   │   └── 📁 pkg/                   # Modelos, Store simulado e Workflow pipeline
│   ├── 📁 pcm/                       # PrescMed (Vite + React + TS + Tailwind + Gemini AI)
│   │   ├── 📄 package.json           # Dependências Node.js isoladas
│   │   └── 📄 README.md
│   └── 📁 keepdocs-workspace/        # KeepDocs Workspace (Vite + React + TS + Tailwind)
│       ├── 📄 package.json           # Dependências Node.js isoladas
│       └── 📄 README.md
│
├── 📁 shared/                        # Módulos Python e utilitários globais compartilhados
│   ├── 📄 __init__.py
│   ├── 📄 context_utils.py           # Cálculo de orçamento de tokens e formatação
│   └── 📄 logger.py                  # Logger unificado com cores e formato JSON
│
├── 📁 tests/                         # Suíte de Testes Automatizados e Avaliações
│   ├── 📁 unit/                      # Testes unitários (pytest)
│   ├── 📁 integration/               # Testes de integração de API
│   └── 📁 eval/                      # Avaliações de segurança e alinhamento (LLM-as-judge)
│
├── 📁 docs/                          # Documentação Técnica e Diagramas do Workspace
│   ├── 📄 architecture.md            # Especificação técnica do repositório
│   └── 📄 mcp_setup_guide.md         # Guia de conexão com clientes de IA
│
├── 📁 inbox/                         # Quarentena de dados brutos e arquivos em triagem
│
├── 📄 pyproject.toml                 # Empacotamento unificado Python (modo editável)
├── 📄 mcp_config.json                # Apontamento de ferramentas MCP para IDEs
├── 📄 run.ps1                        # Script de automação Windows PowerShell
├── 📄 Makefile                       # Comandos de automação Linux/macOS
├── 📄 .gitignore                     # Exclusão de temporários (.venv, node_modules, .env)
└── 📄 README.md                      # Documentação Mestre do Repositório Global
```

---

## 🚀 Como Iniciar

### 1. Pré-requisitos
- Python 3.11+
- Node.js 18+ (Opcional, apenas para UIs em `/projects`)

### 2. Configuração do Ambiente em Um Clique

No Windows (PowerShell):
```powershell
.\run.ps1 setup
```

No Linux / macOS:
```bash
make setup
```

### 3. Configuração de Credenciais
Adicione sua chave de API do Gemini no arquivo `.env`:
```bash
GEMINI_API_KEY=sua_chave_aqui
```

Configuração opcional de persistência de estado:
```bash
BRAIN_STATE_DB_PATH=shared/state/sessions.db
```

### 4. Execução dos Serviços

**Iniciar ecossistema completo (API Gateway + Servidor MCP SSE):**
```powershell
.\run.ps1 dev
```

**Executar a suíte de testes:**
```powershell
.\run.ps1 test
```

---

## 🧩 Protocolo MCP e Integração de IDEs

O arquivo [`mcp_config.json`](file:///mcp_config.json) na raiz do repositório disponibiliza imediatamente as ferramentas para **Google Antigravity**, **Cursor** e **Claude Desktop**:

- `list_workspace_documents` & `get_document_content`: Integração com arquivos e documentos corporativos.
- `bigquery_execute_query` & `bigquery_get_schema`: Consultas e inspeção de dados em larga escala.
- `get_system_health`: Diagnóstico de integridade do workspace.

O Codex CLI e a extensão carregam o servidor remoto `openaiDeveloperDocs` a partir de
[`.codex/config.toml`](.codex/config.toml) quando este projeto está marcado como confiável. O servidor
é público, somente leitura e consulta apenas a documentação oficial da OpenAI; ele não executa
chamadas da API em nome do usuário. Alterações na configuração passam a valer em uma nova sessão
do Codex.

---

## 🔒 Segurança e Guardrails Zero-Trust (OWASP LLM01)
- Todas as mensagens passam por filtragem de injeção de prompt e mascaramento de dados sensíveis (PII) antes de atingir os modelos.
- Operações destrutivas no disco ou em bancos de dados são bloqueadas por padrão e exigem confirmação explícita *Human-in-the-Loop* (HITL).
