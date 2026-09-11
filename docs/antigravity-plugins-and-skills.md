# 🧩 Guia de Plugins e Skills no Antigravity CLI (`agy`)

O **Google Antigravity CLI** foi desenvolvido sob um modelo de extensibilidade aberta. Você pode ampliar as capacidades do agente inteligente instalando módulos empacotados chamados **Plugins** ou criando instruções declarativas em Markdown chamadas **Skills**.

---

## 📦 1. O Modelo de Plugins do Antigravity

Plugins são pacotes com escopo de nomes (*namespaced bundles*) que reúnem habilidades customizadas, subagentes de segundo plano, regras de código, definições de servidores MCP (Model Context Protocol) e hooks de interceptação de eventos em um único ativo instalável e versionável.

### Estrutura de Diretórios de um Plugin Canônico

Quando um plugin é instalado ou importado, seus arquivos são organizados no caminho:
```text
~/.gemini/antigravity-cli/plugins/<plugin_name>/
├── plugin.json                 # Manifesto obrigatório do pacote
├── mcp_config.json             # Servidores MCP integrados (opcional)
├── hooks.json                  # Interceptores pre/post de ferramentas (opcional)
├── skills/                     # Habilidades especializadas (opcional)
├── agents/                     # Definições de subagentes customizados (opcional)
└── rules/                      # Regras e convenções de código (opcional)
```

---

## 📜 2. O Manifesto do Plugin (`plugin.json`)

O arquivo `plugin.json` é o manifesto obrigatório localizado na raiz de qualquer plugin. Ele define a identidade e os metadados do pacote:

```json
{
  "$schema": "https://antigravity.google/schemas/v1/plugin.json",
  "name": "meu-plugin",
  "description": "Uma breve descrição do propósito e capacidades do plugin."
}
```

### Especificação de Campos:

| Campo | Tipo | Obrigatório | Descrição e Regras |
| :--- | :--- | :--- | :--- |
| `name` | String | **Sim** | Nome único do plugin. Deve conter apenas caracteres alfanuméricos, hifens e sublinhados (expressão regular: `^[a-zA-Z0-9-_]+$`). Usado como identificador nos comandos do CLI. |
| `description` | String | Não | Descrição legível por humanos exibida nas listagens do CLI. |
| `$schema` | String | Não | URL do schema oficial para validação e autocompletar em editores: `https://antigravity.google/schemas/v1/plugin.json`. |

---

## 💻 3. Gerenciamento de Plugins via CLI (`agy plugin`)

O CLI expõe o subcomando `plugin` (ou `plugins`) para gerenciar todo o ciclo de vida das extensões:

- **Listar plugins instalados**:
  ```powershell
  agy plugin list
  ```
- **Validar conformidade de um pacote**:
  ```powershell
  agy plugin validate /caminho/para/o/plugin
  ```
- **Instalar um plugin local**:
  ```powershell
  agy plugin install /caminho/para/o/plugin
  ```
- **Desabilitar ou habilitar um plugin sem desinstalar**:
  ```powershell
  agy plugin disable <plugin_name>
  agy plugin enable <plugin_name>
  ```
- **Desinstalar um plugin**:
  ```powershell
  agy plugin uninstall <plugin_name>
  ```

---

## 🎯 4. Agent Skills e Conversão em Slash Commands

Skills são arquivos Markdown declarativos que orientam o agente na execução de tarefas de engenharia específicas com protocolos e ferramentas recomendadas.

> [!IMPORTANT]
> No Antigravity CLI, **todas as Skills registradas convertem-se automaticamente em Slash Commands** no terminal e na interface interativa (TUI). Por exemplo, uma skill nomeada `clean-artifacts` fica imediatamente disponível como `/clean-artifacts`.

### 🔹 Skills de Workspace (Específicas do Projeto)
Armazenadas na pasta `.agents/skills/` na raiz do repositório:
```yaml
---
name: format-tests
description: Padroniza e reformata asserções de testes unitários em Python
---

# Instruções
Ao receber o comando /format-tests, inspecione a pasta tests/ e aplique as correções...
```

### 🔹 Skills Globais (Disponíveis em Qualquer Pasta)
Armazenadas na pasta global de configuração:
```text
~/.gemini/antigravity-cli/skills/
```
Qualquer skill localizada nessa pasta é importada como comando global em qualquer sessão do `agy`.

---

## 🪝 5. Sistema de Hooks de Ciclo de Vida

Hooks interceptam as ações do agente imediatamente antes (`pre`) ou depois (`post`) da execução de ferramentas (por exemplo, executar o formatador de código logo após a ferramenta `write_to_file` modificar um arquivo):
- Definidos no arquivo `hooks.json` do plugin ou nas configurações centrais `settings.json`.
- Inspecionados na interface interativa do terminal pelo comando:
  ```text
  /hooks
  ```

---

## 🌐 6. Integração com Model Context Protocol (MCP)

Plugins podem empacotar seus próprios servidores MCP via `mcp_config.json`, garantindo que ferramentas locais (como parsers de bancos de dados, browsers ou inspectores) sejam provisionadas automaticamente com o pacote sem requerer configuração manual separada.
