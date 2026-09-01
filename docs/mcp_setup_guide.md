# Guia de Configuração e Conexão de Ferramentas MCP

Este guia orienta a integração do servidor de ferramentas unificado FastMCP (`mcp_servers/server.py`) com as principais IDEs e clientes de IA.

---

## 1. Conexão com o Google Antigravity IDE

O Antigravity lê o arquivo `mcp_config.json` localizado na raiz do workspace automaticamente:

```json
{
  "mcpServers": {
    "meu-workspace-tools": {
      "command": "python",
      "args": ["-m", "mcp_servers.server", "--transport", "stdio"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

Para validar a conexão dentro do IDE:
1. Abra a paleta de comandos do Antigravity.
2. Selecione **MCP: Reload Servers**.
3. As ferramentas `bigquery_execute_query`, `list_workspace_documents` e `get_system_health` ficarão imediatamente disponíveis.

---

## 2. Conexão com o Cursor

Abra as configurações do Cursor em **Features > MCP Servers** e adicione:
- **Name:** `meu-workspace-tools`
- **Type:** `command`
- **Command:** `python -m mcp_servers.server --transport stdio`

---

## 3. Conexão com o Claude Desktop

No arquivo `%APPDATA%\Claude\claude_desktop_config.json` (Windows) ou `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "meu-workspace-tools": {
      "command": "python",
      "args": [
        "-m",
        "mcp_servers.server",
        "--transport",
        "stdio"
      ],
      "cwd": "C:/Users/melki/.gemini/antigravity-ide/scratch/meu-workspace-global",
      "env": {
        "PYTHONPATH": "C:/Users/melki/.gemini/antigravity-ide/scratch/meu-workspace-global"
      }
    }
  }
}
```

---

## 4. Execução via Transporte SSE (Porta 8080)

Para ambientes de contêiner ou comunicação cliente-servidor web:
```powershell
.\run.ps1 mcp --transport sse
```
O endpoint estará acessível em: `http://127.0.0.1:8080/sse`

---

## 5. Documentação oficial da OpenAI no Codex

O workspace versiona a configuração do Docs MCP em `.codex/config.toml`:

```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

O Codex carrega configurações de projeto apenas quando o repositório está marcado como confiável.
Para confirmar que o servidor foi reconhecido, execute a partir da raiz:

```powershell
codex mcp list
codex mcp get openaiDeveloperDocs
```

O servidor é público, somente leitura e não chama a API da OpenAI em nome do usuário. Ele fornece
busca e leitura da documentação oficial. Uma sessão já aberta não recebe novas ferramentas
retroativamente; depois de adicionar ou alterar a configuração, abra uma nova sessão do Codex.

Referências oficiais:

- [Docs MCP](https://learn.chatgpt.com/learn/docs-mcp)
- [Configuração por projeto](https://learn.chatgpt.com/docs/config-file/config-basic)
