# 🤖 Guia Operacional: Tarefas em Segundo Plano e Subagentes no Antigravity CLI (`agy`)

O **Google Antigravity CLI** e a plataforma **Antigravity 2.0** adotam uma arquitetura de execução assíncrona multi-threaded. Em vez de bloquear o terminal ou prender a sua sessão interativa durante compilações demoradas, pesquisas amplas na base de código ou testes extensos, o agente principal delega essas operações a **Subagentes** ou **Tarefas de Background (`Tasks`)** paralelas.

---

## ⚡ 1. Modelo de Execução Assíncrona

A delegação assíncrona permite que você continue editando código, inspecionando arquivos e conversando com a IA enquanto threads autônomas em segundo plano executam análises de forma concorrente:

- **Isolamento de Contexto**: Cada subagente inicia com uma janela de contexto limpa, utilizando o tier de modelo configurado (`inherit`, `flash`, ou `pro`), evitando desperdício de tokens na conversa principal.
- **Opções de Workspace**: O subagente pode compartilhar a pasta de trabalho do agente pai (`inherit`), criar uma árvore Git isolada (`branch`) ou compartilhar o armazenamento físico (`share`).
- **Comunicação Inter-Agentes**: Agentes comunicam-se enviando mensagens direcionadas por meio de seus conversation IDs únicos. Enviar uma mensagem para um subagente inativo (`Idle`) reativa-o automaticamente.
- **Limite de Aninhamento**: Há um teto estrito de segurança de até **10 níveis de profundidade** de subagentes para evitar recursão infinita ou exaustão de recursos.

---

## 🎛️ 2. Painel Interativo de Agentes (`/agents`)

O painel de gerenciamento de agentes fornece controle e visibilidade completa sobre a hierarquia de agentes em execução:

### Como Abrir o Painel
Digite `/agents` no prompt do terminal e pressione Enter.

### Informações Exibidas no Painel
- **Identifier**: ID exclusivo do subagente alvo.
- **Role**: Função especializada do agente (ex: `Codebase Researcher`, `Database Debugger`, `Security Auditor`).
- **State**: Estado em tempo real:
  - `Running`: Agente em execução ativa, processando raciocínio ou executando ferramentas.
  - `Idle`: Tarefa concluída, resultado enviado ao agente pai e aguardando novas instruções.
  - `Killed`: Agente encerrado permanentemente (Git worktrees temporárias são limpas automaticamente).
  - `Error`: Falha ou exceção durante a execução.
- **Step**: Resumo em tempo real da ferramenta ou passo de raciocínio atual.

### Inspeção Profunda de Raciocínio (Deep-Dive)
1. No painel `/agents`, utilize as setas `↑` / `↓` para selecionar o subagente desejado.
2. Pressione `Enter` para abrir a **Visão Detalhada do Subagente**.
3. Inspecione o fluxo de pensamentos internos (*thoughts*), chamadas de ferramentas (*tool calls*) e saídas brutas.
4. Pressione `Esc` para retornar ao painel principal de agentes.

---

## 📋 3. Monitoramento de Tarefas com `/tasks`

Para operações de terminal em segundo plano que não envolvem raciocínio agentic direto (como comandos de build, suítes de testes automatizados ou processos de longa duração):

```text
/tasks
```

O comando `/tasks` permite:
- Acompanhar processos em execução sem travar o terminal.
- Selecionar um processo com `↑` / `↓` e pressionar `Enter` para inspecionar os logs de `stdout`/`stderr`.
- Encerrar processos de forma segura caso entrem em loop ou congelem.

---

## ⌨️ 4. Ergonomia e Atalhos de Teclado no Terminal

Para eliminar a fricção de troca de contexto quando um subagente requer autorização de ferramenta ou intervenção:

### 🚀 Navegação "Teleport" (`Alt + J`)
Quando um subagente precisa de aprovação para executar uma ação sensível (ex: escrever um arquivo ou executar um comando shell), uma notificação pisca na barra de status:
1. Pressione **`Alt + J`** diretamente no painel do prompt.
2. Você é instantaneamente "teleportado" para a visão detalhada do subagente que aguarda autorização.
3. Confirme ou rejeite a ação solicitada.
4. Pressione **`Esc`** para teleportar de volta para a sua conversa principal.

### ⚡ Aprovação Instantânea "Fast-Path" (`Ctrl + K`)
Para aprovar a ação de um subagente sem sair do painel ativo:
1. Observe a linha de notificação exibida diretamente acima da caixa de prompt (ex: *"Subagent asks to run 'npm test'"*).
2. Pressione **`Ctrl + K`** para aprovar instantaneamente a ação em background sem abrir sobreposições nem trocar de tela.

---

## 🛠️ 5. Criação de Agentes Customizados em Markdown (`.md`)

O Antigravity CLI descobre agentes customizados declarados em formato Markdown com frontmatter YAML nos seguintes caminhos canônicos:

| Escopo | Localização Canônica |
| :--- | :--- |
| **Workspace (Projeto)** | `.agents/agents/<name>.md` ou `.agents/agents/<name>/agent.md` |
| **Global (Máquina)** | `~/.gemini/config/agents/<name>.md` |
| **Plugins** | `plugins/<plugin_name>/agents/` |

### Estrutura do Frontmatter YAML:

```yaml
---
name: code-auditor
description: Subagente especializado em auditoria de segurança, boas práticas e análise estática.
tools:
  - view_file
  - grep_search
  - find_by_name
  - run_command
subagent: true
mainAgent: false
model: inherit
commandExecutionPolicy: sandbox
---

# System Prompt
Você é um auditor de segurança especializado em arquiteturas Zero-Trust e boas práticas de código.

# Diretrizes
1. Inspecione padrões de código sem aplicar alterações destrutivas sem aprovação.
2. Identifique vulnerabilidades de injeção, vazamento de credenciais e concorrência.
3. Forneça recomendações de remediação claras e objetivas.
```

> [!WARNING]
> Certifique-se de usar nomes canônicos exatos na lista `tools:` (como `view_file`, `replace_file_content`, `run_command`, `grep_search`). Nomes inexistentes ou com erros de digitação podem fazer com que o processo do subagente congele durante a validação.
