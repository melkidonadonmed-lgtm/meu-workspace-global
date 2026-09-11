# 🧩 skills.md — Catálogo Mestre de Habilidades Governadas

> **Catálogo Canônico e Fonte Única da Verdade do Ecossistema.**  
> Todas as habilidades residem sob subpastas dedicadas contendo seu respectivo `SKILL.md` canônico com frontmatter YAML delimitado.  
> Organização Estruturada pelos 7 Bundles Centrais (analytics, arquitetura, auditoria, engenharia, governanca, research, ui-engineering).

---

## 1. Bundle: Dados & Analytics (`skills/analytics/`)

| ID | Versão | Domínio | Caminho Relativo | Gatilhos Principais | Descrição Resumida | Agentes Autorizados |
|---|---|---|---|---|---|---|
| `workspace-data-analytics-architect` | v1.0.0 | analytics | `skills/analytics/workspace-data-analytics-architect/SKILL.md` | `kpi`, `dashboard`, `metricas`, `planilha`, `dados tabulares` | Modelagem analítica, consultas SQL otimizadas e relatórios executivos de dados. | `sql_specialist`, `workspace_specialist` |

---

## 2. Bundle: Arquitetura de Sistemas (`skills/arquitetura/`)

| ID | Versão | Domínio | Caminho Relativo | Gatilhos Principais | Descrição Resumida | Agentes Autorizados |
|---|---|---|---|---|---|---|
| `arquitetura-design-implementacao-sistema` | v1.0.0 | arquitetura | `skills/arquitetura/arquitetura-design-implementacao-sistema/SKILL.md` | `arquitetura de sistema`, `design de sistema`, `c4 model`, `diagrama arquitetural` | Design de alto nível, decomposição em micro-módulos e diagramas técnicos. | `orchestrator`, `code_consistency_specialist` |
| `project-enhancer-brainstorm` | v1.0.0 | arquitetura | `skills/arquitetura/project-enhancer-brainstorm/SKILL.md` | `brainstorm`, `melhorias de projeto`, `ideacao arquitetural` | Exploração criativa de novas funcionalidades e escalabilidade de projetos. | `orchestrator`, `research_evolution_specialist` |

---

## 3. Bundle: Auditoria & Consistência de Código (`skills/auditoria/`)

> **Diretiva de Negative Bounds:** As habilidades de auditoria operam estritamente sobre projetos em `projects/*`. É terminantemente proibido auditar a raiz (`meu-workspace-global`), a pasta `agents/` ou o catálogo `skills/` (`AUDIT_TARGET_PROHIBITED`).

| ID | Versão | Domínio | Caminho Relativo | Gatilhos Principais | Descrição Resumida | Agentes Autorizados |
|---|---|---|---|---|---|---|
| `code-validator` | v1.0.0 | auditoria | `skills/auditoria/code-validator/SKILL.md` | `valide este código`, `audite este código`, `analise o risco deste código`, `linha a linha` | Auditoria linha a linha de código-fonte, expansão de contexto e matriz causal de risco (%). | `code_consistency_specialist` |
| `code-reviewer` | v1.0.0 | auditoria | `skills/auditoria/code-reviewer/SKILL.md` | `review`, `revisar`, `revisar código`, `revisar pr` | Revisão sistemática de pull requests, tipagem estrita, legibilidade e segurança. | `code_consistency_specialist` |
| `api-auditor` | v1.0.0 | auditoria | `skills/auditoria/api-auditor/SKILL.md` | `check`, `test`, `audit`, `url`, `api`, `auditar`, `testar api` | Auditoria e verificação de endpoints REST/SSE, códigos HTTP, latência e segurança. | `code_consistency_specialist` |
| `skill-repo-analyser` | v2.0.0 | auditoria | `skills/auditoria/skill-repo-analyser/SKILL.md` | `analise estas pastas soltas`, `reorganize meu repositório`, `organize meu workspace` | Varredura em pastas soltas, mapeamento de dependências e plano de arquitetura modular. | `workspace_specialist`, `code_consistency_specialist` |
| `web-security-auditor` | v1.0.0 | auditoria | `skills/auditoria/web-security-auditor/SKILL.md` | `auditoria de seguranca`, `security audit`, `checklist seguranca web`, `owasp checklist` | Checklist de segurança para Web Apps (OWASP Top 10, segredos, XSS, CSRF, CSP). | `security_guard` |

---

## 4. Bundle: Engenharia & Infraestrutura (`skills/engenharia/`)

| ID | Versão | Domínio | Caminho Relativo | Gatilhos Principais | Descrição Resumida | Agentes Autorizados |
|---|---|---|---|---|---|---|
| `managing-python-dependencies` | v1.0.0 | engenharia | `skills/engenharia/managing-python-dependencies/SKILL.md` | `uv`, `poetry`, `pip`, `venv`, `dependencias python`, `pyproject.toml` | Gestão determinística de pacotes Python via `uv` com isolamento de ambiente virtual. | `workspace_specialist`, `code_consistency_specialist` |
| `developing-with-streamlit` | v1.0.0 | engenharia | `skills/engenharia/developing-with-streamlit/SKILL.md` | `streamlit`, `st.components`, `dashboard streamlit`, `app streamlit` | Desenvolvimento de dashboards interativos e protótipos de dados em Python com Streamlit. | `workspace_specialist`, `html_modular_specialist` |
| `mcp-troubleshooter-design-advisor` | v1.0.0 | engenharia | `skills/engenharia/mcp-troubleshooter-design-advisor/SKILL.md` | `mcp`, `fastmcp`, `servidor mcp`, `sse`, `stdio` | Diagnóstico, correção e arquitetura de servidores Model Context Protocol (FastMCP). | `code_consistency_specialist`, `orchestrator` |
| `brain-mcp-inspector` | v1.0.0 | engenharia | `skills/engenharia/brain-mcp-inspector/SKILL.md` | `brain mcp inspector`, `inspecionar mcp`, `brain-mcp`, `json-rpc inspect` | Monitoramento e inspeção de payloads JSON-RPC em tempo real na barreira de ferramentas. | `security_guard`, `orchestrator` |

---

## 5. Bundle: Governança & Orquestração (`skills/governanca/`)

| ID | Versão | Domínio | Caminho Relativo | Gatilhos Principais | Descrição Resumida | Agentes Autorizados |
|---|---|---|---|---|---|---|
| `skill-factory` | v1.0.0 | governanca | `skills/governanca/skill-factory/SKILL.md` | `criar skill`, `nova skill`, `importar skill`, `salvar skill` | Criação canônica, sanitização de slugs e registro atômico de novas habilidades no catálogo. | `skill-factory`, `orchestrator` |
| `skill-healthcheck` | v1.0.0 | governanca | `skills/governanca/skill-healthcheck/SKILL.md` | `saude do catalogo`, `healthcheck`, `auditar skills` | Auditoria de integridade do catálogo: YAML válido, convenções kebab-case e links. | `skill-factory`, `orchestrator` |
| `skill-requirements-analyzer` | v1.0.0 | governanca | `skills/governanca/skill-requirements-analyzer/SKILL.md` | `analise de requisitos`, `requisitos de skill` | Decomposição formal de demandas em requisitos funcionais e não-funcionais. | `orchestrator`, `execution_planner` |
| `order-request-router` | v1.0.0 | governanca | `skills/governanca/order-request-router/SKILL.md` | `rotear pedido`, `triagem de pedido`, `classificar intencao` | Triagem hierárquica e cálculo do modo de execução ideal (Direct, Single, Cascade). | `orchestrator`, `router` |
| `resilience-circuit-breaker` | v1.0.0 | governanca | `skills/governanca/resilience-circuit-breaker/SKILL.md` | `disjuntor`, `circuit breaker`, `deadlock`, `timeout` | Sentinela de resiliência impedindo loops infinitos, deadlocks e exaustão de contexto. | `orchestrator` |
| `validacao-pre-entrega` | v1.0.0 | governanca | `skills/governanca/validacao-pre-entrega/SKILL.md` | `pre-entrega`, `relatorio de ganho`, `score de qualidade` | Checklist de auditoria final e verificação de qualidade antes da entrega ao usuário. | `orchestrator`, `code_consistency_specialist` |
| `git-automator-and-configurator` | v1.0.0 | governanca | `skills/governanca/git-automator-and-configurator/SKILL.md` | `git commit`, `git push`, `branches`, `repositorio git`, `conventional commits` | Automação de versionamento Git com Conventional Commits e controle de branches. | `code_consistency_specialist` |
| `auto-asset-backup` | v1.0.0 | governanca | `skills/governanca/auto-asset-backup/SKILL.md` | `backup de ativos`, `backup de skills`, `backup drive` | Rotinas de backup automatizado para Google Drive e arquivos de ativos. | `orchestrator` |
| `accidental-data-loss-prevention` | v1.0.0 | governanca | `skills/governanca/accidental-data-loss-prevention/SKILL.md` | `apagar`, `deletar`, `excluir`, `rm -rf`, `drop table`, `operacao destrutiva` | Portão Zero-Trust com confirmação humana obrigatória (HITL) contra ações destrutivas. | `security_guard`, `orchestrator` |
| `aprimoramento-expansibilidade-agentes-skills` | v1.0.0 | governanca | `skills/governanca/aprimoramento-expansibilidade-agentes-skills/SKILL.md` | `expansibilidade`, `aprimorar agentes`, `novas capacidades` | Metodologia de expansão contínua de capacidades cognitivas e arquitetura de subagentes. | `orchestrator`, `skill-factory` |
| `skill-context-expander-guard` | v1.0.0 | governanca | `skills/governanca/skill-context-expander-guard/SKILL.md` | `expansao de contexto`, `guardrail de contexto` | Prevenção de estouro de tokens e isolamento estrito de memória operacional. | `orchestrator`, `security_guard` |
| `skill-context-sentinel-state` | v1.0.0 | governanca | `skills/governanca/skill-context-sentinel-state/SKILL.md` | `sentinela de estado`, `context state` | Rastreamento do estado conversacional e persistência transacional em SQLite WAL. | `orchestrator` |

---

## 6. Bundle: Pesquisa Técnica & Modelos (`skills/deep-research-hub/`)

| ID | Versão | Domínio | Caminho Relativo | Gatilhos Principais | Descrição Resumida | Agentes Autorizados |
|---|---|---|---|---|---|---|
| `deep-research` | v1.0.0 | research | `skills/deep-research-hub/deep-research/SKILL.md` | `pesquisa profunda`, `web search`, `relatorio aprofundado` | Investigação exaustiva na web aberta com validação cruzada de fontes e citações. | `research_evolution_specialist` |
| `notebooklm` | v1.0.0 | research | `skills/deep-research-hub/notebooklm/SKILL.md` | `notebooklm`, `audio overview`, `consultar notas`, `caderno notebooklm` | Integração de cadernos de notas e documentos fontes com geração de Audio Overviews. | `research_evolution_specialist` |

---

## 7. Bundle: UI Engineering & Design System (`skills/ui-engineering/`)

| ID | Versão | Domínio | Caminho Relativo | Gatilhos Principais | Descrição Resumida | Agentes Autorizados |
|---|---|---|---|---|---|---|
| `accessibility` | v1.0.0 | ui-engineering | `skills/ui-engineering/accessibility/SKILL.md` | `acessibilidade`, `a11y`, `wcag`, `aria`, `contraste` | Validação de conformidade WCAG 2.1 AA, contraste de cores e tags semânticas. | `html_modular_specialist` |
| `responsive-html-ui-master` | v1.0.0 | ui-engineering | `skills/ui-engineering/responsive-html-ui-master/SKILL.md` | `responsivo`, `mobile-first`, `menu movel`, `layout fluido` | Design e codificação de páginas fluidas, menus mobile e responsividade touchscreen. | `html_modular_specialist` |
| `react-vite-tailwind-architect` | v1.0.0 | ui-engineering | `skills/ui-engineering/react-vite-tailwind-architect/SKILL.md` | `react`, `vite`, `tailwind`, `shadcn`, `hooks react`, `indexeddb` | Arquitetura de aplicações React 18+ com Vite, Tailwind CSS e persistência IndexedDB. | `html_modular_specialist`, `pcm` |
| `frontend-design` | v1.0.0 | ui-engineering | `skills/ui-engineering/frontend-design/SKILL.md` | `design`, `layout`, `interface`, `componente`, `tela` | Criação de layouts modernos, hierarquia visual e design system. | `html_modular_specialist` |
| `frontend-ui-designer` | v1.0.0 | ui-engineering | `skills/ui-engineering/frontend-ui-designer/SKILL.md` | `designer ui`, `prototipagem`, `componente visual`, `mockup ui` | Prototipagem e especificação visual de componentes de interface de usuário. | `html_modular_specialist` |
| `frontend-auditor` | v1.0.0 | ui-engineering | `skills/ui-engineering/frontend-auditor/SKILL.md` | `frontend auditor`, `auditar frontend`, `revisar interface` | Auditoria especializada de interfaces e detecção de desalinhamentos de design. | `html_modular_specialist` |
| `color-palette-and-depth-architect` | v1.0.0 | ui-engineering | `skills/ui-engineering/color-palette-and-depth-architect/SKILL.md` | `paleta de cores`, `gradiente`, `profundidade`, `tema dark` | Sistemas de cor dinâmicos, gradientes suaves, elevação e profundidade tátil. | `html_modular_specialist` |
| `minimal-ui-menu-icon-architect` | v1.0.0 | ui-engineering | `skills/ui-engineering/minimal-ui-menu-icon-architect/SKILL.md` | `menu minimalista`, `sidebar`, `dock`, `navbar`, `icone svg` | Menus retráteis, docks flutuantes e ícones SVG minimalistas com física tátil. | `html_modular_specialist` |
| `tactile-hyperreal-ui-auditor` | v1.0.0 | ui-engineering | `skills/ui-engineering/tactile-hyperreal-ui-auditor/SKILL.md` | `tatil`, `hiper-realista`, `4k feel`, `sombras`, `acabamento premium` | Direção de arte Obsidian & Gold, micro-emboss e sombras multicamadas. | `html_modular_specialist` |
| `ui-auditor-tactile-design-architect` | v1.0.0 | ui-engineering | `skills/ui-engineering/ui-auditor-tactile-design-architect/SKILL.md` | `ui auditor tactile`, `tactile design`, `arquitetura tatil` | Auditoria profunda e arquitetura tátil de interfaces para a plataforma WAOE. | `html_modular_specialist` |
| `design-interface-medica-minimalista` | v1.0.0 | ui-engineering | `skills/ui-engineering/design-interface-medica-minimalista/SKILL.md` | `medico`, `prontuario`, `prescricao`, `clinica`, `cfm`, `a4` | Telas clínicas minimalistas, receituários A4, doses pediátricas e Resolução CFM. | `pcm`, `html_modular_specialist` |
| `skill-html-modular-builder` | v1.0.0 | ui-engineering | `skills/ui-engineering/skill-html-modular-builder/SKILL.md` | `montagem de pages`, `montagem html`, `construir tela html` | Montador de páginas HTML5 modulares com zero placeholders. | `html_modular_specialist` |
| `ui-component-auditor` | v1.0.0 | ui-engineering | `skills/ui-engineering/ui-component-auditor/SKILL.md` | `auditar html`, `auditar ui`, `blueprint de refatoracao` | Diagnóstico de HTML/CSS legado gerando blueprints técnicos de refatoração. | `html_modular_specialist` |
| `ui-refactor-implementer` | v1.0.0 | ui-engineering | `skills/ui-engineering/ui-refactor-implementer/SKILL.md` | `refatorar html`, `implementar blueprint`, `modularizar html` | Aplicação de tokens de design e componentização em código legado. | `html_modular_specialist` |
| `curadoria-fontes-design-repositorios` | v1.0.0 | ui-engineering | `skills/ui-engineering/curadoria-fontes-design-repositorios/SKILL.md` | `curadoria fontes`, `design repositorios`, `fontes design` | Seleção de tipografias e referências em repositórios de design de elite. | `html_modular_specialist` |
| `google-maps-platform` | v1.0.1 | ui-engineering | `skills/ui-engineering/google-maps-platform/SKILL.md` | `maps`, `google maps`, `geocoding`, `autocomplete`, `address validation` | Implementação de mapas interativos, locais, rotas e geocodificação usando Google Maps Platform APIs. | `html_modular_specialist`, `pcm` |
| `luxury-tactile-ui-architect` | v1.0.0 | ui-engineering | `skills/ui-engineering/luxury-tactile-ui-architect/SKILL.md` | `luxo`, `ouro`, `obsidian`, `tátil`, `emboss` | Direção de arte Luxury Obsidian & Brushed Gold, física de materiais, glassmorphism e widgets táteis. | `html_modular_specialist` |
| `waoe-ui-ux-auditor` | v1.0.0 | ui-engineering | `skills/ui-engineering/waoe-ui-ux-auditor/SKILL.md` | `auditoria ux`, `heuristica`, `nielsen`, `wcag 2.2` | Auditoria heurística modular, validação funcional de fluxos complexos e otimização tátil de front-end. | `html_modular_specialist` |

---

## 8. Habilidades Adicionais e Utilitários

| ID | Versão | Domínio | Caminho Relativo | Gatilhos Principais | Descrição Resumida | Agentes Autorizados |
|---|---|---|---|---|---|---|
| `skill-prompt-generator` | v1.1.0 | governanca | `skills/skill-prompt-generator/SKILL.md` | `gere um prompt`, `meta-prompt`, `otimize meu prompt`, `tags xml` | Engenharia de prompts para agentes autônomos utilizando tags XML canônicas. | `skill-factory`, `orchestrator` |
| `check-updates` | v1.0.0 | engenharia | `skills/check-updates/SKILL.md` | `check for updates`, `am I up to date`, `what version`, `update skills` | Verificação de versão instalada e atualização de pacotes de habilidades. | `workspace_specialist` |
