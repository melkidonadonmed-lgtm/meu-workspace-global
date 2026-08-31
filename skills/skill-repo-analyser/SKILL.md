---
name: skill-repo-architecture-analyser
version: 2.0.0
description: Analisador, Arquitetor e Reorganizador de Repositório Global. Realiza varredura profunda em pastas e caminhos soltos, mapeia dependências e redundâncias, detecta potenciais conflitos de código e gera um plano determinístico de montagem de um repositório global, modular e escalável.
triggers:
  - "analise estas pastas soltas"
  - "reorganize meu repositório"
  - "crie um plano de migração de código"
  - "organize meu workspace"
  - "monte uma estrutura global de repositório"
---

# SKILL.md — Analisador, Arquitetor e Reorganizador de Repositório Global (`skill-repo-architecture-analyser`)

## Metadados da Habilidade
- **Nome:** Global Repository Architect & Structural Conflict Preventer
- **Versão:** 2.0.0
- **Categoria:** Engenharia de Software, Arquitetura de Sistemas e Gestão de Repositórios
- **Finalidade:** Realizar a varredura profunda em pastas e caminhos soltos/fragmentados, mapear dependências e redundâncias, detectar potenciais conflitos de código e gerar um plano determinístico de montagem de um repositório global, modular, escalável e de fácil leitura por diferentes modelos de IA e equipes.
- **Gatilhos de Ativação:** "analise estas pastas soltas", "reorganize meu repositório", "crie um plano de migração de código", "organize meu workspace", "monte uma estrutura global de repositório".

---

## Entradas Requeridas
- `raw_paths`: Lista de caminhos absolutos ou relativos das pastas/arquivos soltos a serem analisados.
- `target_workspace_root`: Diretório raiz onde a nova estrutura global será consolidada.
- `tech_stack_hints` (opcional): Linguagens e frameworks principais (ex.: Python, Node.js, Next.js, Go, Docker).

---

## Fluxo Operacional de Execução em 4 Fases

### Fase 1: Varredura Diagnóstica & Inventário de Ativos
Ao receber os caminhos brutos (`raw_paths`):
1. **Mapeamento de Arquivos:** Catalogue a árvore de arquivos identificando extensões, scripts de automação, documentações, dados brutos e arquivos de configuração.
2. **Triagem de Elementos Críticos:**
   - Repositórios Git locais e históricos de versão (`.git`).
   - Habilidades e prompts de IA (`SKILL.md`, `system_prompts`).
   - Códigos-fonte e módulos de aplicação (`.py`, `.ts`, `.js`, `.go`).
   - Artefatos de build e temporários (`node_modules`, `__pycache__`, `.venv`, `.env`).
3. **Detecção de Anomalias:** Identifique arquivos duplicados (por nome e hash), scripts órfãos e arquivos soltos sem contexto.

### Fase 2: Mapeamento de Dependências & Diagnóstico de Conflitos
Antes de propor qualquer movimentação, analise os riscos estruturais:
1. **Conflitos de Importação e Namespaces:** Mapeie referências cruzadas de código para prevenir quebras de rotas e dependências relativas de linguagem (ex.: `PYTHONPATH` ou aliasing `@/`).
2. **Conflitos de Dependência e Lockfiles:** Verifique divergências entre gerenciadores de pacotes (ex.: convivência acidental de `package-lock.json`, `pnpm-lock.yaml` ou `uv.lock`).
3. **Colisão de Nomes e Poluição de Contexto:** Identifique arquivos com nomes idênticos em pastas diferentes e evite estruturas monolíticas que causem sobrecarga de contexto (*context bloat*) para agentes de IA.

### Fase 3: Plano de Arquitetura Alvo (Estrutura Global)
Estruture a nova árvore de diretórios do repositório aplicando o princípio de **separação estrita de responsabilidades**:
- `/agents` → Hub central de agentes, roteadores e orquestradores.
- `/skills` → Catálogo reutilizável de habilidades modulares contendo arquivos `SKILL.md`.
- `/projects` → Aplicações e frontends isolados (ex.: clientes Next.js/React).
- `/mcp_servers` → Servidores e ferramentas de integração do Model Context Protocol (FastMCP/Stdio/SSE).
- `/configs` → Manifestos YAML, schemas JSON, regras de guardrails e variáveis de ambiente exemplo (`.env.example`).
- `/tests` → Suíte unificada de testes unitários, integração e avaliação (*evals*).
- `/docs` → Documentação técnica, guias rápidos e diagramas do repositório.
- `/raw_data` ou `/inbox` → Dados brutos e arquivos temporários em triagem.

### Fase 4: Matriz de Migração 'De -> Para' & Roteiro de Execução
Gere o plano de ação sequencial dividido em:
1. **Fase 0: Preparação e Backup:** Garantia de segurança antes de qualquer movimento físico.
2. **Matriz Mapeada 'De -> Para':** Tabela relacionando a localização original de cada pasta/arquivo e seu novo destino padronizado.
3. **Scripts de Automação de Migração:** Comandos de terminal (PowerShell / Bash) para mover os arquivos preservando o histórico Git e ignorando temporários.
4. **Plano de Atualização de Imports:** Ajustes necessários no código para que os caminhos continuem funcionando perfeitamente.

---

## Restrições Negativas e Zonas de Risco (O que NÃO fazer)

- ❌ **NUNCA executar movimentações físicas de arquivos diretamente:** Esta Skill gera o **plano e os scripts de auditoria**. A execução dos comandos depende de confirmação explícita (*Human-in-the-Loop*).
- ❌ **NUNCA apagar arquivos brutos ou originais:** Todos os arquivos marcados como duplicados ou obsoletos devem ser movidos para uma pasta temporária de quarentena (`/archive` ou `/raw_data`), nunca deletados definitivamente.
- ❌ **NUNCA incluir pastas de temporários/build no plano de migração:** Pastas como `node_modules`, `.venv`, `.next` e `dist` devem ser ignoradas no script de transporte e recriadas no novo ambiente via gerenciador de pacotes.
- ❌ **NUNCA utilizar caminhos absolutos rígidos nas configurações:** Toda a nova estrutura deve ser projetada com caminhos relativos ao diretório raiz para garantir portabilidade entre diferentes sistemas operacionais.

---

## Formato Obrigatório de Saída

Ao ser acionada, esta Skill deve estruturar a resposta rigorosamente no seguinte formato:

### 1. Diagnóstico do Cenário Atual
- Resumo em tópicos dos ativos encontrados nas pastas soltas, volume de arquivos, linguagens e problemas de organização identificados.

### 2. Matriz de Conflitos e Riscos Identificados
| Componente / Pasta | Risco de Conflito | Tipo de Conflito | Ação Preventiva Recomendada |
|---|---|---|---|
| `exemplo/pasta_a` | Alto | Conflito de Namespace / Import | Padronizar pacotes editáveis (`pip install -e .`) e caminhos absolutos |
| `exemplo/lockfiles` | Médio | Divergência de Lockfile | Padronizar um único gerenciador de pacotes no projeto alvo |

### 3. Diagrama da Estrutura Global Alvo (Visão ASCII)
- Representação gráfica clara da nova árvore de diretórios proposta para o `target_workspace_root`.

### 4. Matriz Mapeada de Migração ("De -> Para")
| Item Original | Destino Alvo Padronizado | Função no Repositório Global |
|---|---|---|
| `[Caminho_Original_1]` | `/agents/orchestrator.py` | Orquestrador principal do ecossistema |
| `[Caminho_Original_2]` | `/skills/skill-exemplo/SKILL.md` | Habilidade modular de IA |

### 5. Script de Automação e Plano de Verificação
- Código completo em PowerShell ou Bash para execução da migração.
- Comandos de teste (ex.: `pytest`, `npm run build`) para validar se a aplicação compila sem caminhos quebrados após a migração.

---

## Exemplo de Entrada do Usuário
```text
[Caminhos Soltos]: C:\Users\Dev\Desktop\projeto_antigo, C:\Users\Dev\Downloads\novas_skills, C:\Users\Dev\Documents\script_teste.py
[Diretório Alvo]: C:\Users\Dev\Projects\meu-workspace-global
```
