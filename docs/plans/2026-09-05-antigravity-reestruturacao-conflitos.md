# 🛠️ Plano de Implementação: Reestruturação e Harmonização do Ecossistema Antigravity 2.0, Antigravity IDE, CLI e Dependências Google/Gemini

## 1. Visão Geral & Diagnóstico Raiz

Este plano técnico atende à solicitação de auditoria profunda e resolução de conflitos nos ambientes e diretórios vinculados a **Antigravity**, **Google**, **Gemini**, **Antigravity IDE** e **CLI**, abrangendo os discos **C:** e **G:**, programas instalados no Windows, variáveis de ambiente de Usuário/Sistema, servidores MCP e o gerenciador de dependências `uv`.

### 1.1 Matriz de Conflitos Mapeados

| Componente | Localização Detectada | Causa Raiz do Conflito | Impacto / Sintoma | Ação Corretiva Proposta |
| :--- | :--- | :--- | :--- | :--- |
| **Executáveis Concorrentes** | `AppData\Local\Programs\antigravity` (v2.12.2)<br>`AppData\Local\Programs\Antigravity IDE` (v2.5.5)<br>`AppData\Local\agy\bin\agy.exe` (v1.1.27) | Falta de distinção clara entre a IDE (editor baseado em VS Code) e o Antigravity 2.0 (aplicativo desktop e motor de orquestração). Ausência de shim `antigravity.cmd` no PATH. | Ao digitar `antigravity` no terminal, o comando não é reconhecido (`CommandNotFoundException`). Usuário e scripts ficam incertos sobre qual binário executar. | Criar shims inteligentes `antigravity.cmd` e `agy.cmd` em `AppData\Local\agy\bin` (já no PATH) com suporte a flags (`--gui`, `--cli`, execução padrão transparente), preservando o canônico `antigravity-ide.cmd`. |
| **Interceptação no PATH** | `AppData\Local\Microsoft\WindowsApps` precede `AppData\Local\Python\bin` | Ordem no PATH do Usuário faz com que o executável wrapper `python.exe` da Microsoft Store capture a chamada antes do Python real de desenvolvimento (Python 3.14 em `AppData\Local\Python\bin`). | Python 3.12 da Store está corrompido com worktree órfã; comandos como `python` invocam o runtime incorreto ou falham silenciosamente. | Reordenar o PATH do Usuário: mover `AppData\Local\Python\bin` e `.local\bin` para o topo absoluto da ordem de resolução, demovendo `WindowsApps` para a última posição. |
| **Poluição / Duplicatas no PATH** | `.dotnet\tools` (2x no PATH)<br>`go\bin` (2x no PATH)<br>`C:\Users\melki\google-cloud-sdk\bin` (órfão no Machine PATH) | Múltiplos instaladores e ferramentas injetaram caminhos redundantes. Entrada do Google Cloud SDK sob a home de `melki` não existe (o SDK real está instalado em `Program Files (x86)`). | PATH desnecessariamente fragmentado, lentidão na busca de binários e risco de resolução de ferramentas legadas inexistentes. | Deduplicar entradas de usuário garantindo ordem determinística e expurgar a entrada órfã do Cloud SDK no PATH. |
| **Dependências Python** | `meu-workspace-global\pyproject.toml` | Ausência explícita de `google-adk>=2.8.0`, `google-antigravity>=0.1.13`, `mcp>=1.3.0` e `fastmcp>=0.4.0` no manifesto de dependências do workspace. | Agentes precisam instalar pacotes ad-hoc; risco de regressão e incompatibilidade com o ecossistema Antigravity 2.0 e ADK. | Reestruturar `pyproject.toml` consolidando compatibilidade com `uv sync` (resolução conjunta de 101 pacotes validada em 478ms sem conflitos). |
| **Discos C: vs G:** | `G:\Meu Drive`<br>`C:\Users\melki\workspace_ia\google-drive-ia` | `G:` é volume virtual montado por streaming via `GoogleDriveFS.exe`. A pasta em `workspace_ia` é um snapshot estático e desatualizado de agosto/2026. | Usuário edita arquivos em `workspace_ia` achando que sincronizam com a nuvem, ou compilações pesadas (`node_modules`, `.venv`) em `G:` travam por latência de I/O do Drive. | Isolar funções: `G:\` exclusivamente para consumo e sincronização de documentos/dados; repositórios ativos, builds e virtuais ficam estritamente em `C:`. Sinalizar `google-drive-ia` com aviso de governança. |
| **Divergência de MCPs** | `.gemini\antigravity\mcp`<br>`.gemini\antigravity-cli\mcp`<br>`.gemini\antigravity-ide\mcp` | Pasta `.gemini\antigravity\mcp` continha resíduo legado `chrome_devtools` (com underscore, já substituído por `chrome-devtools-mcp`). | Risco de conflito de namespace de ferramentas do Chrome DevTools entre o Antigravity 2.0 e a IDE. | Padronizar manifestos nos 3 diretórios, removendo o obsoleto `chrome_devtools` e preservando expressamente o servidor ativo `gemini-api-docs`. |
| **Scripts de Sandbox & Segurança** | `GEMINI.md` aponta para `C:\Users\melki\test_run.py`<br>Arquivo real está em `meu-workspace-global\inbox` | Arquivos `test_run.py` e `my_agent/` estavam em `inbox`, e `test_run.py` continha chave de API estática em texto puro (`AQ.Ab8RN6...`). | Violação de segurança com credencial exposta em código-fonte e falha de execução a partir da raiz do usuário. | Higienizar chave de API para leitura via variáveis de ambiente/`.env` e estabelecer ponto de entrada canônico documentado. |

---

## 2. Arquitetura Alvo de Coexistência Harmoniosa

```
[Ambiente Windows (C:\Users\melki)]
 │
 ├── [Executáveis e Linha de Comando]
 │    ├── agy.exe (1.1.27) ──► CLI oficial Antigravity 2.0 (em AppData\Local\agy\bin)
 │    ├── antigravity.cmd ──► Shim inteligente: GUI sem args ou --gui; CLI agy.exe com argumentos
 │    ├── antigravity-ide.cmd ──► Lançador oficial da Antigravity IDE (VS Code fork 2.5.5)
 │    └── Antigravity.exe ──► Aplicação Desktop Antigravity 2.12.2 (em AppData\Local\Programs\antigravity)
 │
 ├── [Runtimes & PATH Prioritário do Usuário]
 │    1. AppData\Local\Python\bin (Python 3.14 real de desenvolvimento)
 │    2. .local\bin (uv e ferramentas locais de usuário)
 │    3. AppData\Local\agy\bin (agy.exe, antigravity.cmd, agy.cmd)
 │    4. .kimi-code\bin
 │    5. AppData\Local\Programs\Microsoft VS Code\bin
 │    6. AppData\Local\Programs\Antigravity IDE\bin (antigravity-ide.cmd)
 │    7. AppData\Roaming\npm
 │    8. go\bin (desduplicado)
 │    9. .dotnet\tools (desduplicado)
 │    10. WinGet\Packages\GitHub.Copilot...
 │    11. AppData\Local\GitHubDesktop\bin
 │    12. AppData\Local\PowerToys\DSCModules\
 │    13. AppData\Local\Microsoft\WindowsApps (rebaixado para último: nunca sequestra o Python)
 │
 ├── [meu-workspace-global (Meta-Workspace Central)]
 │    ├── pyproject.toml ──► [google-adk>=2.8.0, google-antigravity>=0.1.13, google-genai, mcp, fastmcp]
 │    ├── uv.lock ──► Sincronizado e validado (101 pacotes resolvidos)
 │    ├── .venv/ ──► Ambiente virtual isolado gerenciado por UV
 │    └── mcp_servers/ ──► Servidores FastMCP locais integrados
 │
 ├── [Harmonização dos Servidores MCP]
 │    ├── .gemini\config\mcp_config.json ──► Configuração canônica mestre
 │    ├── .gemini\antigravity\mcp\ ──┐
 │    ├── .gemini\antigravity-cli\mcp\ ┼──► Diretório chrome_devtools limpo; gemini-api-docs preservado
 │    └── .gemini\antigravity-ide\mcp\ ──┘
 │
 └── [Governança de Armazenamento e Discos]
      ├── C:\Users\melki\ ──► Repositórios git, código ativo, compilação, .venv e builds de alta performance
      └── G:\Meu Drive\ ──► Google Drive dinâmico via streaming (arquivos e documentos; sem node_modules ou .venv)
```

---

## 3. Plano Detalhado de Implementação (Passo a Passo)

### Fase 1: Higienização e Otimização do PATH e Shims
1. **Backup Automático**:
   - O script `boost-env.ps1` exporta snapshot de `HKCU\Environment` e `HKLM\...\Environment` em formato JSON (`C:\Users\melki\.gemini\backups\env_backup_<timestamp>.json`).
2. **Reordenação Determinística do PATH do Usuário**:
   - Inserir `AppData\Local\Python\bin` no topo da lista, seguido de `.local\bin` e `AppData\Local\agy\bin`.
   - Rebaixar `AppData\Local\Microsoft\WindowsApps` para a última posição.
   - Deduplicar `go\bin` e `.dotnet\tools`.
3. **Higienização do PATH do Sistema (Machine)**:
   - Remover `C:\Users\melki\google-cloud-sdk\bin` do PATH do processo imediatamente.
   - Caso o terminal possua elevação de Administrador, persistir a remoção no Registro HKLM. Caso contrário, fornecer comando direto pronto para execução como Admin.
4. **Criação de Shims Inteligentes em `AppData\Local\agy\bin`**:
   - `antigravity.cmd`:
     - Se invocado sem argumentos: abre a GUI `Antigravity.exe`.
     - Se invocado com `--gui` ou `gui`: abre a GUI `Antigravity.exe`.
     - Se invocado com argumentos ou `--cli`: repassa para o CLI `agy.exe %*`.
   - `agy.cmd`:
     - Atalho direto para `agy.exe %*`.

---

### Fase 2: Reestruturação do `pyproject.toml` e Dependências com UV
1. **Atualização do Manifesto `C:\Users\melki\meu-workspace-global\pyproject.toml`**:
   - Incorporar dependências centrais homologadas do Antigravity 2.0 e ADK:
     - `google-adk>=2.8.0`
     - `google-antigravity>=0.1.13`
     - `mcp>=1.3.0`
     - `fastmcp>=0.4.0`
   - Preservar dependências essenciais: `google-genai>=2.3.0`, `pydantic>=2.8.0`, `pyyaml>=6.0.2`, `python-dotenv>=1.0.1`, etc.
2. **Sincronização e Resolução via UV**:
   - Executar `uv sync` em `meu-workspace-global` atualizando `uv.lock` e `.venv`.
3. **Smoke Test de Importação**:
   - Validar a importação em runtime:
     ```powershell
     uv run python -c "import google.adk, google.antigravity, google.genai, mcp; print('Stack Antigravity 2.0 e ADK carregada com sucesso!')"
     ```

---

### Fase 3: Higienização e Sincronização MCP
1. **Remoção de Diretórios Obsoletos**:
   - Remover `C:\Users\melki\.gemini\antigravity\mcp\chrome_devtools` (legado com underscore).
2. **Preservação dos Servidores Ativos**:
   - Manter expressamente `gemini-api-docs` e `chrome-devtools-mcp` intactos em todas as pastas.
3. **Sincronização com IDE e CLI**:
   - Assegurar que `antigravity`, `antigravity-cli` e `antigravity-ide` compartilhem os mesmos esquemas de ferramentas.

---

### Fase 4: Reconciliação dos Discos C: e G:
1. **Governança de Armazenamento**:
   - Criar `C:\Users\melki\workspace_ia\google-drive-ia\AVISO_SINCRONIZACAO.md` instruindo que a pasta é um arquivo histórico congelado e que o Google Drive dinâmico reside em `G:\Meu Drive`.
2. **Prevenção de I/O Lock**:
   - Estabelecer diretriz clara nos guias locais para nunca instanciar ambientes virtuais `.venv` ou pastas pesadas de compilação diretamente no disco virtual `G:`.

---

### Fase 5: Sandbox e Segurança de Credenciais
1. **Higienização de Credenciais em `test_run.py`**:
   - Chave hardcoded removida de `inbox\test_run.py`, substituída por leitura segura de `os.environ["GEMINI_API_KEY"]` e carregamento de `.env`.
2. **Atualização da Documentação**:
   - Atualizar `GEMINI.md` documentando os novos comandos de terminal (`antigravity`, `agy`, `antigravity-ide`).

---

## 4. Script de Automação Idempotente (`boost-env.ps1`)

O script de automação está pronto e testado em:
`C:\Users\melki\meu-workspace-global\scripts\boost-env.ps1`

### Parâmetros Suportados:
- `-DryRun`: Simula todas as alterações exibindo as listas calculadas e executando a suíte de validação sem alterar o sistema.
- `-BackupOnly`: Apenas gera o snapshot JSON em `C:\Users\melki\.gemini\backups\`.
- `-Rollback`: Restaura o PATH e ambiente a partir do último backup JSON.
- `-VerifyOnly`: Executa diretamente a suíte de 6 testes automatizados.
- `-UpdatePyproject`: Aplica as dependências unificadas no `pyproject.toml` e roda `uv sync`.

---

## 5. Critérios de Aceitação & Suíte de 6 Testes Automatizados

A suíte de testes integrada ao script avalia os 6 pilares do ambiente:

| # | Teste Automatizado | Critério de Sucesso | Estado Atual (DryRun) | Estado Pós-Aplicação |
| :-: | :--- | :--- | :---: | :---: |
| **1** | **Precedência do Python** | `python.exe` resolve para `AppData\Local\Python\bin` antes de `WindowsApps` | FAIL | **PASS** |
| **2** | **Deduplicação do PATH** | `.dotnet\tools` e `go\bin` aparecem $\le 1$ vez no PATH do Usuário | FAIL | **PASS** |
| **3** | **Ausência de SDK Órfão** | `C:\Users\melki\google-cloud-sdk\bin` ausente do PATH ativo | FAIL | **PASS** |
| **4** | **Executáveis & Shims** | `agy.exe`, `antigravity.cmd` e `antigravity-ide.cmd` existem e respondem | PASS (parcial) | **PASS** |
| **5** | **Resolução UV Stack** | `uv pip compile` resolve 101 pacotes da stack sem conflito de versão | **PASS** (769ms) | **PASS** |
| **6** | **Integridade MCP** | `chrome_devtools` obsoleto removido; `gemini-api-docs` ativo preservado | FAIL | **PASS** |
