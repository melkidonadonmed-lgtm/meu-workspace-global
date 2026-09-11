# 🚀 Modo Headless do Antigravity CLI (`agy`) — Guia de Automação e Referência Técnica

O **Modo Headless** (também chamado de *Print Mode*) permite executar o agente **Google Antigravity CLI (`agy`)** de forma não-interativa e programática. Ele envia um ou mais prompts para o modelo, captura e processa a resposta em formatos legíveis por máquina e finaliza a execução.

Esse modo é essencial para:
- Integrações em pipelines de CI/CD (GitHub Actions, GitLab CI, Azure DevOps).
- Scripts de automação em PowerShell (`.ps1`) e Python (`.py`).
- Extração de dados estruturados com JSON Schema.
- Sessões contínuas de alta performance com streaming via `stdin`.

---

## 📌 1. Executando um Prompt Único (`-p` / `--print`)

Passe um prompt com `-p` (ou seus aliases `--print` e `--prompt`) para executar uma única vez e encerrar:

```powershell
agy -p "Em uma frase, o que é um git rebase?"
```

```text
O git rebase reescreve o histórico de commits movendo uma sequência de commits para um novo commit base, mantendo um histórico estritamente linear.
```

### Separação entre `stdout` e `stderr`
- **`stdout`**: Recebe estritamente a resposta gerada pelo modelo.
- **`stderr`**: Recebe diagnósticos, avisos de progresso, alertas de autenticação e logs operacionais.

Dessa forma, você pode capturar a resposta em uma variável limpa no PowerShell:
```powershell
$resposta = (agy -p "Liste três ferramentas populares de CI/CD separadas por vírgula.")
Write-Host "Resultado capturado: $resposta"
```

> [!NOTE]
> O modo headless reutiliza credenciais cacheadas previamente. Caso uma sessão não esteja autenticada em ambiente sem terminal interativo (como CI), o CLI encerra imediatamente com erro informando a necessidade de autenticação.

---

## 📊 2. Formatos de Saída (`--output-format`)

O parâmetro `--output-format` define a formatação do `stdout`:

| Formato | Estrutura de `stdout` | Cenário de Uso Recomendado |
| :--- | :--- | :--- |
| `text` | Texto simples sem envelopamento (padrão) | Scripts rápidos e visualização direta |
| `json` | Um único objeto JSON emitido na conclusão | Extração de resposta e metadados de tokens/tempo |
| `stream-json` | Eventos JSON delimitados por nova linha (NDJSON) | Monitoramento em tempo real de chamadas de ferramentas e tokens |

### 🔹 2.1 Formato JSON

Gera um envelope completo contendo métricas de uso e status:

```powershell
agy -p "Em uma frase, o que é um git cherry-pick?" --output-format json | ConvertFrom-Json
```

#### Envelope de Resposta:
```json
{
  "conversation_id": "055a398f-db14-4c5f-abbb-1bf03f8120a7",
  "status": "SUCCESS",
  "response": "O git cherry-pick aplica as alterações introduzidas por um commit específico existente em outra branch no branch atual.\n",
  "duration_seconds": 6.88,
  "num_turns": 1,
  "usage": {
    "input_tokens": 10415,
    "output_tokens": 657,
    "thinking_tokens": 616,
    "cache_read_tokens": 8113,
    "total_tokens": 11072
  }
}
```

Campos do envelope JSON:
- `conversation_id`: Identificador único da sessão para continuar posteriormente.
- `status`: Estado terminal (`SUCCESS`, `ERROR`, `CANCELED`, `INTERRUPTED`).
- `response`: Texto de resposta emitido pelo agente.
- `error`: Mensagem de erro (presente apenas em falhas).
- `duration_seconds`: Tempo total de execução em segundos.
- `num_turns`: Quantidade de turnos de diálogo na conversa.
- `structured_output`: Objeto parseado (quando utilizado `--json-schema`).
- `json_schema`: O schema aplicado.
- `usage`: Contadores de tokens (`input_tokens`, `output_tokens`, `thinking_tokens`, `cache_read_tokens`, `total_tokens`).

### 🔹 2.2 Saída Estruturada com JSON Schema (`--json-schema`)

Permite restringir o retorno a uma estrutura rígida validada pelo modelo:

```powershell
agy -p "Extraia a versão semântica v3.12.1 nos campos inteiros major, minor e patch." `
  --output-format json `
  --json-schema '{"type":"object","properties":{"major":{"type":"integer"},"minor":{"type":"integer"},"patch":{"type":"integer"}},"required":["major","minor","patch"]}' | ConvertFrom-Json
```

O resultado parseado estará disponível diretamente na propriedade `structured_output`.

---

## ⚡ 3. Streaming em Tempo Real (`stream-json`)

Quando especificado `--output-format stream-json`, o CLI emite um fluxo NDJSON linha a linha:

```powershell
agy -p "Em uma frase, o que é git stash?" --output-format stream-json
```

O ciclo de vida do fluxo emite:
1. `{"event":"init", ...}`: Informa o diretório de trabalho (`cwd`), ferramentas disponíveis (`tools`) e modo de permissão.
2. `{"event":"step_update", ...}`: Notificações parciais de passos, fragmentos incrementais de texto (`text_delta`) e chamadas de ferramentas (`tool_name`, `tool_info`).
3. `{"event":"result", ...}`: Evento final consolidado com o status terminal e estatísticas acumuladas.

---

## 🔄 4. Conversação Contínua Multi-Turn via `stdin` (`--input-format stream-json`)

Para criar aplicações interativas de alta performance que realizam múltiplos turnos sem reiniciar o processo nem perder o contexto cacheado:

```bash
agy --input-format stream-json --output-format stream-json
```

Envie mensagens no formato JSON por linha para o `stdin`:
```json
{"event":"user","message":{"content":"Qual é a capital do Brasil?"}}
```

Após o CLI responder com `result`, envie a próxima pergunta mantendo o processo aberto:
```json
{"event":"user","message":{"content":"Qual é a população dessa cidade?"}}
```

### Vantagens do Streaming via `stdin`:
- **Latência Mínima**: O processo não é reiniciado entre perguntas, economizando até 80% do tempo de inicialização.
- **Cache Warmed-Up**: As árvores de contexto e ferramentas já permanecem carregadas em memória.
- **Encerramento Elegante**: Basta fechar o fluxo `stdin` para que o processo conclua o turno ativo e saia com código `0`.

---

## 🛡️ 5. Permissões e Segurança no Modo Headless

Como não há prompt interativo para pedir confirmação ao usuário, a política de execução segue o modelo Zero-Trust:
- Operações de leitura/escrita no workspace ativo são permitidas por padrão conforme as diretivas do projeto.
- Chamadas de ferramentas com efeitos colaterais (como comandos de terminal) são suaves-negadas (*soft-denied*) por padrão a menos que estejam explicitadas no arquivo de configuração:
  [`C:\Users\melki\.gemini\antigravity-cli\settings.json`](file:///C:/Users/melki/.gemini/antigravity-cli/settings.json) sob `permissions.allow`.
- Para autorizar todas as ferramentas em ambientes controlados/sandboxed, utilize a flag:
  `--dangerously-skip-permissions`.

---

## 📋 6. Tabela de Referência de Flags

| Flag | Padrão | Descrição |
| :--- | :--- | :--- |
| `-p`, `--print`, `--prompt` | — | Executa um prompt único não-interativamente e finaliza. |
| `--output-format` | `text` | Formato de saída: `text`, `json`, `stream-json`. |
| `--input-format` | `text` | Formato de entrada: `text`, `stream-json` (escuta via stdin). |
| `--json-schema` | — | String ou caminho de arquivo `.json` para impor resposta estruturada. |
| `--model` | — | Slug do modelo (consulte modelos disponíveis com `agy models`). |
| `--effort` | — | Esforço de raciocínio: `low`, `medium`, `high`. |
| `--agent` | — | Agente especializado para a execução (consulte com `agy agents`). |
| `-c`, `--continue` | `false` | Continua o contexto da conversa mais recente. |
| `--conversation` | — | Retoma uma conversa específica pelo ID. |
| `--dangerously-skip-permissions` | `false` | Auto-aprova solicitações de ferramentas em pipelines confiáveis. |
| `--print-timeout` | `5m` | Tempo limite máximo de espera pela resposta. |
| `--sandbox` | `false` | Executa com restrições rígidas de sandbox no terminal. |
