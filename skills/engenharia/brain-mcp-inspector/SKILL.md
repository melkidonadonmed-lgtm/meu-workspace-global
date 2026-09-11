---
name: brain-mcp-inspector
description: Implementa e opera o servidor MCP (Model Context Protocol) nativo do ecossistema Brain — expõe `.brain/state/sessions.db` (checkpoints e auditoria) como recursos/ferramentas MCP somente-leitura via transporte `stdio` ou `SSE` (com autenticação Bearer/JWT opcional), e inicia um servidor local efêmero para pré-visualizar artefatos HTML em `.brain/artifacts/`. Use para conectar hosts MCP (Claude Desktop, Claude Code, Cursor) ou agentes remotos ao estado do workspace. NÃO usar para diagnosticar falhas de conexão/tool-calling de servidores MCP de terceiros (ver `mcp-troubleshooter-design-advisor`) nem para gravar checkpoints (este servidor é somente-leitura — ver `brain-state-orchestrator`).
triggers:
  - "brain mcp inspector"
  - "inspecionar mcp"
  - "brain-mcp"
  - "json-rpc inspect"
  - "monitorar mcp"
---

# Brain MCP Inspector (`brain-mcp-inspector`)

Servidor MCP nativo (JSON-RPC 2.0) que expõe o estado persistido do ecossistema Brain a qualquer host compatível. Suporta dois transportes: `stdio` (processo filho local — Claude Desktop, Claude Code, Cursor) e `SSE`/Streamable HTTP (agentes remotos, com autenticação Bearer/JWT obrigatória sempre que exposto além de `127.0.0.1`). É estritamente somente-leitura sobre `.brain/state/sessions.db` — nunca grava checkpoints ou audita eventos (isso é papel de `brain-state-orchestrator` e `resilience-circuit-breaker`).

### Gatilhos de Ativação
- Conexão automática na inicialização de um host MCP configurado para este servidor (`stdio`).
- Invocação de ferramentas via chat: "listar últimos checkpoints", "inspecionar estado da sessão X", "abrir servidor local de artefatos".
- Leitura direta de recursos por URI: `brain://state/latest`, `brain://artifacts/explorer`.
- Necessidade de conectar um agente ou ferramenta remota via rede (`--transport sse`).
- **Não ativar** para depurar por que um servidor MCP de terceiros não conecta ou não expõe tools — isso é `mcp-troubleshooter-design-advisor`.

---

## 1. Princípios e Diretrizes Técnicas

- **Somente leitura, sempre:** este servidor nunca faz `INSERT`/`UPDATE`/`DELETE` em `sessions.db` — apenas `SELECT`. Gravar estado é escopo exclusivo de `brain-state-orchestrator` (checkpoints) e `resilience-circuit-breaker` (auditoria).
- **Um único núcleo de despacho:** `MCPCoreEngine.process_request()` é o ÚNICO lugar que interpreta métodos JSON-RPC e ferramentas — os transportes `stdio` (`run_stdio`) e `SSE` (`MCPHttpHandler.do_POST`) apenas encaminham para ele. Nunca duplique lógica de dispatch dentro de um handler de transporte.
- **`stdio` é local e confiável; `SSE` não é.** `stdio` roda como processo filho do próprio host MCP — sem superfície de rede, sem necessidade de autenticação. `SSE` escuta uma porta TCP; por isso a autenticação Bearer/JWT é obrigatória sempre que `--host` não for loopback (`127.0.0.1`/`localhost`/`::1`) — o servidor recusa iniciar nesse caso sem um segredo configurado.
- **Sem segredo padrão embutido:** `--secret`/`BRAIN_AUTH_SECRET` nunca tem um valor de fallback no código. Um segredo fixo e visível no repositório tornaria qualquer token forjável por quem lesse o código-fonte.
- **`sessions.db` é compartilhado:** o mesmo arquivo é escrito por `brain-state-orchestrator` (tabelas `checkpoints`/`transition_audit`) e por `resilience-circuit-breaker` (`circuit_breaker_audit`). Este servidor pode rodar antes de qualquer um dos dois ter gravado algo — todas as consultas verificam se a tabela existe antes de ler, em vez de assumir que ela já foi criada.
- **Zero dependências externas:** stdlib do Python 3.10+ (`http.server.ThreadingHTTPServer`, `sqlite3`, `hmac`, `hashlib`, `base64`, `queue`, `threading`). Nenhum `pip install` na raiz do repositório.

---

## 2. Fluxo Operacional Passo a Passo

### Entradas Esperadas
- Mensagens JSON-RPC 2.0 (`initialize`, `resources/list`, `resources/read`, `tools/list`, `tools/call`, `notifications/initialized`) via `stdin` (stdio) ou `POST /messages` (SSE).
- Parâmetros de ferramentas: `session_id` (str, `get_session_details`), `limit` (int, padrão 5, `list_checkpoints`), `port` (int, padrão 8765, `open_visual_artifact_server`), `open_browser` (bool, padrão `true`).

### Passos
1. **Handshake:** `initialize` responde com `protocolVersion`, `capabilities` (`resources`, `tools`) e `serverInfo`.
2. **Descoberta:** `resources/list` e `tools/list` declaram os 2 recursos e as 3 ferramentas disponíveis (schemas completos embutidos no código, nunca inventados pelo host).
3. **Leitura de recurso:** `resources/read` com `brain://state/latest` retorna o `state_blob` do checkpoint mais recente; `brain://artifacts/explorer` retorna o HTML de `workspace_explorer.html` (ou um comentário placeholder se o arquivo ainda não existir).
4. **Execução de ferramenta:** `tools/call` despacha para `list_checkpoints`, `get_session_details` ou `open_visual_artifact_server`, sempre via `MCPCoreEngine`.
5. **Servidor de artefatos:** `open_visual_artifact_server` sobe um `HTTPServer` estático em thread daemon apontando para `.brain/artifacts/`, idempotente (uma segunda chamada retorna `ALREADY_RUNNING` em vez de tentar religar a porta).
6. **Transporte SSE:** `GET /sse` abre um stream (`text/event-stream`) por sessão com heartbeat a cada 15s; `POST /messages?session_id=...` injeta uma mensagem, responde `202 ACCEPTED` de imediato e entrega o resultado real de forma assíncrona pelo stream correspondente.

### Erros Comuns
- **Porta em uso (`Address already in use`):** passe outra `--port`/`"port"` — nunca assumido automaticamente.
- **Stream JSON-RPC corrompido em modo `stdio`:** só ocorre se algo além de `run_stdio()` escrever em `sys.stdout`. Toda mensagem de log usa `logging` (configurado para `stream=sys.stderr`), nunca `print()`.
- **`database is locked`:** infrequente aqui pois este servidor só faz `SELECT`, mas se ocorrer sob concorrência pesada com os outros dois motores, é responsabilidade deles (que já usam WAL + `busy_timeout`), não deste inspector.
- **`401 Unauthorized` em `/sse` ou `/messages`:** o servidor foi iniciado com um segredo configurado e o cliente não enviou `Authorization: Bearer <token>` (ou `?token=`), ou o token é inválido/expirado. Gere um novo com `--generate-token`.

### Scripts Disponíveis
- `scripts/mcp_server.py` — servidor completo. `python .agents/skills/brain-mcp-inspector/scripts/mcp_server.py --transport stdio` (padrão) ou `--transport sse [--host 127.0.0.1] [--port 8000] [--secret <segredo>]`. Gerar token de teste: `--generate-token --secret <segredo>` (imprime e encerra).
- `scripts/launch_ecosystem.sh` — atalho: `launch_ecosystem.sh stdio` ou `launch_ecosystem.sh sse [porta]` (sempre em `127.0.0.1`, sem autenticação; para bind público ou Bearer/JWT, invoque `mcp_server.py` diretamente).
- `references/mcp_launcher.json` — modelo de configuração de cliente MCP (variante `stdio` local e `sse` remota) para adaptar ao host usado (Claude Desktop, Cursor, etc.).

---

## 3. Formato de Saída Obrigatório

Resposta padrão de chamada de ferramenta (JSON-RPC 2.0), aqui para `list_checkpoints`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"checkpoints\": [ ... ]\n}"
      }
    ]
  }
}
```

Bloqueio de autenticação (transporte SSE, quando um segredo está configurado):

```json
{
  "jsonrpc": "2.0",
  "error": {"code": -32001, "message": "Nao autorizado: token Bearer ausente."}
}
```

---

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)

- **NUNCA** faça bind em um host que não seja loopback (`127.0.0.1`/`localhost`/`::1`) sem um segredo de autenticação configurado — o próprio `main()` recusa iniciar nesse caso; não contorne essa checagem.
- **NUNCA** use um segredo padrão/hardcoded no código para assinar ou validar tokens — exija sempre `--secret` ou `BRAIN_AUTH_SECRET` explícitos.
- **NUNCA** compare assinaturas HMAC com `==`; use sempre `hmac.compare_digest` (proteção contra timing attack), como já faz `JWTManager.verify_token`.
- **NUNCA** grave, atualize ou apague linhas em `sessions.db` a partir deste servidor — qualquer necessidade de escrita pertence a `brain-state-orchestrator` ou `resilience-circuit-breaker`.
- **NUNCA** escreva em `sys.stdout` fora de `run_stdio()`/`main()` quando o transporte for `stdio` — corrompe o canal do protocolo.
- **NUNCA** implemente um segundo dispatcher de métodos JSON-RPC dentro de um handler de transporte; sempre delegue a `MCPCoreEngine.process_request()`.
- **NUNCA** imprima ou logue o conteúdo de tokens/segredos fora do fluxo explícito de `--generate-token`.
