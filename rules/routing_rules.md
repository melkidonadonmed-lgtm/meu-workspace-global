# 🧭 Routing Rules: Critérios Determinísticos de Roteamento & Despacho Cognitivo

> **Versão:** 1.0.0  
> **Status:** Ativo & Obrigatório  
> **Componente Responsável:** `AutoSkillRouter` (`agents/router.py`)

---

## 1. Modos de Execução do Roteador

O `AutoSkillRouter` classifica cada requisição em um dos 4 modos de execução fundamentais:

| Modo de Execução | Gatilho / Condição | Comportamento do Orquestrador |
| :--- | :--- | :--- |
| **`HITL_BLOCK`** | Presença de termos destrutivos (`apagar`, `drop table`, `rm -rf`) | Interrompe o fluxo imediatamente e solicita confirmação explícita do usuário. |
| **`DIRECT_RESPONSE`** | Saudações triviais (`olá`, `bom dia`, `ok`) ou conversas sem demanda técnica | Resposta direta sem carregar skills no prompt para economizar tokens. |
| **`SINGLE_SKILL`** | Demanda técnica pontual com 1 habilidade ou agente de alta pontuação | Injeção cirúrgica da skill específica ou despacho direto para o subagente responsável. |
| **`MULTI_AGENT_CASCADE`** | Projetos complexos, refatorações, criação de sistemas do zero | O `MasterOrchestrator` coordena em cascata múltiplos subagentes especialistas. |

---

## 2. Separação de Alvos: Subagente Especialista vs. Skill de Catálogo

Para evitar injeção desnecessária de texto no contexto do modelo:

1. **Subagentes Especialistas (`AGENT_TARGETS`)**:
   - São módulos de código executável com lógica própria (`SqlSpecialistAgent`, `HTMLModularSpecialistAgent`, `CustomerIssueReviewerAgent`, `WorkspaceSpecialistAgent`, `ResearchEvolutionSpecialistAgent`).
   - O orquestrador despacha a tarefa **diretamente para o método Python/Go do agente**, sem ler o arquivo Markdown como texto de instrução.
2. **Skills de Catálogo (`SKILL.md`)**:
   - São pacotes de conhecimento declarativo (`SKILL.md`).
   - O orquestrador lê o conteúdo da skill sob demanda (Progressive Disclosure) e o injeta como System Prompt temporário.

---

## 3. Matriz de Especialização e Despacho Automático (TDAH Friendly)

O sistema foi desenhado para **ativação zero-memory**: o operador não precisa se lembrar de comandos específicos. O roteador avalia palavras-chave e intenções semânticas:

```mermaid
graph TD
    Input[Entrada do Usuário] --> CheckDestructive{Operação Destrutiva?}
    CheckDestructive -- Sim --> Block[HITL_BLOCK: Interceptação de Segurança]
    CheckDestructive -- Não --> Router[AutoSkillRouter: Classificação Semântica]
    
    Router -->|SQL / BigQuery / Schemas| SQL[SqlSpecialistAgent]
    Router -->|HTML5 / UI Modular / Telas| HTML[HTMLModularSpecialistAgent]
    Router -->|Chamados / Bugs / Issues| Issue[CustomerIssueReviewerAgent (ADK Go v2)]
    Router -->|Pastas / Google Drive / Scan| WS[WorkspaceSpecialistAgent]
    Router -->|Pesquisa Profunda / Investigação| Research[ResearchEvolutionSpecialistAgent]
    Router -->|Demanda Complexa sem Skill| Gap[SkillFactory: Auto-Geração de Skill]
```

---

## 4. Tratamento de Gaps Operacionais (Skill Gap Fallback)

Se a requisição for classificada como **COMPLEXA**, mas nenhuma skill existente no catálogo atender à demanda:
1. O `MasterOrchestrator` detecta um *Gap Operacional*.
2. Aciona automaticamente a **`SkillFactory`** (via `ResearchEvolutionSpecialistAgent`).
3. Uma nova habilidade padronizada (`SKILL.md`) é gerada, validada e registrada dinamicamente no catálogo antes da execução final.
