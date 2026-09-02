# Meta-Workspace Global (Agent Orchestration Engine)

Ambiente operacional universal de orquestração de agentes autônomos, catálogo de skills governadas e barramento MCP, projetado para analisar, projetar, auditar e desenvolver qualquer projeto de software alvo.

## Linguagem Ubíqua

**Meta-Workspace**:
O ambiente e plataforma global de orquestração cognitiva que provê agentes, ferramentas e skills para manipular qualquer base de código.
_Avoid_: Monólito, Aplicação específica, Projeto individual

**Projeto Alvo (Target Project)**:
Qualquer repositório, sistema ou base de código externa sobre a qual o Meta-Workspace opera para auditar, desenvolver ou refatorar.
_Avoid_: Submódulo embutido, Projeto legado

**MasterOrchestrator**:
Coordenador central stateful responsável pelo ciclo de vida, persistência transacional de sessões e execução de fluxos multi-agente.
_Avoid_: Controlador, Backend genérico

**AutoSkillRouter**:
Roteador determinístico de intenções que classifica complexidade, seleciona skills governadas e aplica barreiras de segurança (guardrails) antes da execução.
_Avoid_: Switch-case, Parser de intenção simples

**Skill**:
Unidade atômica ou bundle governado de conhecimento procedimental (`SKILL.md`), instruções e scripts consumidos progressivamente por agentes.
_Avoid_: Script solto, Plugin genérico

**Subagente Especializado**:
Agente autônomo com foco de domínio estrito e ferramentas delimitadas (ex: segurança, SQL, workspace, UI), orquestrado pelo MasterOrchestrator.
_Avoid_: Worker genérico, Thread de fundo

**Barramento MCP (Tool Bus)**:
Camada padronizada de ferramentas locais e remotas (FastMCP) para integração com GCP, Google Workspace, APIs e sistemas de arquivos sob sandboxing.
_Avoid_: Client SDK manual, RPC customizado

**Workspace Path Binding**:
Mecanismo de acoplamento dinâmico por sessão que fixa o escopo de execução dos agentes e ferramentas MCP à raiz do projeto alvo ativo.
_Avoid_: Diretório hardcoded, Contexto global estático

**Memória Híbrida de Projeto**:
Estratégia de persistência que divide o conhecimento: decisões de domínio e glossário vivem no projeto alvo, enquanto histórico transacional e checkpoints residem na base do Meta-Workspace.
_Avoid_: Base de dados monolítica única, Estado volátil apenas em memória

**Topologia Hub-and-Spoke**:
Padrão de coordenação centralizada onde o MasterOrchestrator gerencia o plano e despacha tarefas para subagentes sem comunicação direta peer-to-peer.
_Avoid_: Rede autônoma sem mestre, Malha P2P não coordenada

**Checkpoint de Resiliência**:
Ponto de restauração atômico em controle de versão (Git) criado antes de mutações de código, restaurado automaticamente caso o disjuntor desarme.
_Avoid_: Backup manual de arquivos, Estado não versionado

**Gateway SSE Híbrido**:
Ponto de entrada unificado para streaming de eventos e comandos de agentes via HTTP/SSE na porta 8000 e FastMCP na porta 8080.
_Avoid_: Polling contínuo, WebSocket despadronizado

**SkillFactory**:
Motor de scaffolding e geração padronizada de novas skills com templates declarativos e metadados de governança.
_Avoid_: Criação manual ad-hoc, Gerador de script genérico

**SkillHealthChecker**:
Verificador de integridade que audita a conformidade do frontmatter YAML, links e acoplamentos de skills antes da publicação no catálogo.
_Avoid_: Linter genérico, Validador de sintaxe simples

**Guardrail Zero-Trust**:
Portão de segurança determinístico que bloqueia ou exige autorização humana (HITL) para ações destrutivas ou que violem regras de integridade.
_Avoid_: Validador simples, Middleware comum
