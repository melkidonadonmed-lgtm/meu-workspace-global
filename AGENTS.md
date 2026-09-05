# AGENTS.md — meu-workspace-global

Idioma oficial: **Português (BR)** — código, documentação, commits e respostas.

## O que este repositório é

Workspace de ferramentas para **trabalhar em outros projetos** — ele não é, ele mesmo, o projeto-alvo. Evite auditar ou "melhorar" este próprio repositório quando o pedido for sobre um projeto em `projects/*`.

O código real dos clientes vive fora daqui, em `C:\Users\melki\Projetos\`; as pastas em `projects/` são só symlinks de conveniência.

| Projeto | Symlink | Tech Stack | Repositório GitHub |
|---|---|---|---|
| PresCMed (PCM) | `projects/pcm` | React 18, Vite, TypeScript, Tailwind, IndexedDB | `melkidonadonmed-lgtm/PCM` |
| PresCMed Remix (variante) | `projects/remix-prescmed-new` | React, Vite, TypeScript | `melkidonadonmed-lgtm/remix-prescmed-new` |
| Canvas IDE | `projects/canvas_ide` | React, Vite, TypeScript, Tailwind, Canvas API | `melkidonadonmed-lgtm/canvas_ide` |
| KeepDocs Workspace | `projects/keepdocs-workspace` | React, TypeScript, Streamlit, Python | `melkidonadonmed-lgtm/keepdocs-v2` |
| WAOE | `projects/WAOE` | React, TypeScript, Tailwind | `melkidonadonmed-lgtm/agents-md-95` |

## Como o trabalho acontece

O Claude Code é quem executa aqui, através dos seus próprios mecanismos nativos:
- **Skill tool**: carrega `.claude/skills/*/SKILL.md` sob demanda, pela descrição de cada skill. O catálogo de domínio em `skills/` (auditoria, ui-engineering, engenharia) é real e reflete trabalho já feito.
- **Agent tool**: despacha para subagentes definidos em `.claude/agents/*.md`, quando existirem.

Não há um orquestrador separado por trás disso — nenhum processo Python precisa estar rodando para uma skill ou subagente funcionar.

## O que sobrou do framework Python antigo

Em 2026-09-05, além da camada de serviço (`run.ps1`, API Gateway, servidor MCP), foi auditado item a item o que restava de `agents/*.py`: o que só simulava decisão via texto hardcoded ou dependia de um `GEMINI_API_KEY` que nunca chega a ser chamado por ninguém foi apagado (`orchestrator.py`, `dispatcher.py`, `router.py`, a parte de planejamento do `execution_planner.py`, e os especialistas `sql_specialist.py`, `html_modular_specialist.py`, `customer_issue_reviewer.py`, `research_evolution_specialist.py` — todos com saída fixa/fake quando testados de verdade).

O que tinha lógica determinística real, sem LLM, testada e sobrevivendo sozinha, ficou:
- `agents/specialized/security_guard.py` — `ProjectBoundaryGuardrail` (bloqueia auto-auditoria da raiz/`agents/`/`skills/`) e `SecurityGuardAgent` (detecção de prompt injection, mascaramento de PII/CPF/e-mail, redação de API keys vazadas).
- `agents/specialized/workspace_specialist.py` — varredura real de árvore de arquivos e detecção de stack tecnológica.
- `agents/specialized/code_consistency_specialist.py` — análise AST real de Python (erros de sintaxe, convenção `except Exception` sem `# noqa: BLE001`, compatibilidade de contratos/assinaturas).
- `agents/project_resolver.py` — `ProjectTargetResolver`, extraído do `execution_planner.py`: resolve nome casual de projeto → caminho real em `projects/` + stack detectada.

Nenhum desses é invocado automaticamente — são utilitários Python reais, testados (`tests/unit/`), disponíveis para uso direto ou como script bundlado numa skill (ex: a `audit-project` já reaproveita o mesmo tipo de checagem manualmente).

## Convenções

- Operações destrutivas (deletar, sobrescrever, `rm -rf`, force-push) exigem confirmação explícita antes de executar.
- Skills de governança (auditoria de catálogo, criação de skill) deveriam ficar escopadas a este projeto. **Pendência conhecida:** hoje `~/.claude/skills` ainda aponta globalmente para `Brain/.agents/skills`, então essas skills disparam em qualquer repositório aberto nesta máquina — não só aqui.
