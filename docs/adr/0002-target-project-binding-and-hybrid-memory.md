# 0002. Vinculação Dinâmica de Projetos Alvo e Estratégia de Memória Híbrida

Decidimos adotar a vinculação dinâmica por sessão (*Workspace Path Binding*) para fixar o escopo dos agentes no projeto alvo ativo (seja local em `projects/` ou externo) e uma estratégia de memória híbrida que divide artefatos de domínio e telemetria de sessão.

## Contexto e Motivação

Atualmente, os projetos em desenvolvimento estão localizados no diretório local `projects/`, mas a arquitetura foi concebida para operar sobre quaisquer projetos futuros externos. Precisamos garantir que:
1. O agente saiba exatamente em qual raiz de projeto está atuando, sem correr o risco de poluir o código do Meta-Workspace com arquivos do projeto ou vice-versa.
2. O conhecimento acumulado sobre o projeto seja preservado mesmo se o projeto for versionado ou transferido de máquina.

## Decisão

1. **Workspace Path Binding**: Toda sessão de orquestração recebe e vincula um `workspace_path`. Os subagentes e ferramentas FastMCP restringem suas operações relativas a essa raiz. Projetos locais em `projects/<nome>` são tratados com as mesmas regras que projetos em caminhos externos.
2. **Memória Híbrida**:
   - **Artefatos de Domínio**: `CONTEXT.md`, diagramas e ADRs específicos do projeto alvo são gravados na árvore do próprio projeto alvo, garantindo rastreabilidade no controle de versão (Git).
   - **Estado Transacional**: Snapshots de execução, checkpoint de rollback, logs e métricas do orquestrador são persistidos no banco SQLite global (`shared/state/sessions.db`).
3. **Sandboxing e Guardrails**: Comandos que possam alterar arquivos fora da raiz vinculada ou executar operações destrutivas no projeto alvo são interceptados pelo portão Zero-Trust antes de qualquer execução.
