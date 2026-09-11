# 🪟 Guia de Instalação, Configuração e Autenticação no Windows: Antigravity CLI (`agy`)

Este documento consolida as instruções canônicas para instalação, parametrização avançada e gerenciamento de autenticação segura do **Google Antigravity CLI (`agy`)** no sistema operacional Windows.

---

## 📂 1. Diretório Canônico de Instalação no Windows

No Windows, o instalador oficial registra o executável e seus utilitários diretamente no diretório do usuário ativo:

```text
C:\Users\<username>\AppData\Local\agy\bin
```
*(onde `<username>` representa o perfil do usuário ativo no Windows, correspondente à variável de ambiente `%LOCALAPPDATA%\agy\bin`)*.

### Arquivos Presentes no Diretório de Binários:
- `agy.exe`: O binário executável nativo do Antigravity CLI compilado para Windows (`windows_amd64` ou `windows_arm64`).
- `antigravity.cmd`: Script em lote de compatibilidade para permitir a execução via prompt tradicional `cmd.exe` ou scripts legados.

---

## ⚡ 2. Métodos de Instalação Oficiais

### 🔹 Opção A: PowerShell (Recomendado)
Abra uma sessão do **PowerShell** (5.1 ou PowerShell 7 / `pwsh`) e execute:

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
```

### 🔹 Opção B: Prompt de Comando (CMD)
Abra um **Command Prompt** padrão e execute o comando de download e inicialização autolimpante:

```cmd
curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd
```

---

## 🛠️ 3. Flags de Customização de Instalação

Ao executar os scripts de instalação, você pode anexar as seguintes flags de controle:

| Flag | Finalidade e Comportamento |
| :--- | :--- |
| `--skip-aliases` | **Ignora a limpeza de aliases do shell**: Impede que o script de instalação remova ou substitua aliases existentes de `agy` ou `antigravity` no seu perfil de shell (`$PROFILE`). |
| `--skip-path` | **Ignora a adição ao PATH**: Impede que o script modifique as variáveis de ambiente dinâmicas do perfil de shell, permitindo gerenciar o `PATH` manualmente. |
| `--dir <caminho>` | **Diretório customizado de destino**: Especifica um caminho alternativo para a instalação dos binários em vez do padrão `%LOCALAPPDATA%\agy\bin`. |

### Exemplo de Instalação com Flags no PowerShell:
```powershell
& ([scriptblock]::Create((irm https://antigravity.google/cli/install.ps1))) --skip-aliases --skip-path
```

---

## 🔐 4. Fluxos de Autenticação e Credenciais Seguras

O Antigravity CLI utiliza perfis de token e credenciais seguras para se comunicar com o harness de agentes do Google.

### 🔑 4.1 Login Silencioso via Chaveiro Nativo (Silent Keyring Sign-In)
Ao iniciar o `agy` na sua máquina local, o CLI tenta acessar o **Windows Credential Manager (CredMan)**, o chaveiro seguro nativo do Windows:
- Se um perfil de token válido for localizado no Credential Manager, o CLI **autentica a sessão de forma 100% silenciosa**, sem necessidade de intervenção manual nem abertura de navegador.
- Essa abordagem elimina fricção em tarefas automatizadas, pipelines locais e sessões contínuas no terminal.

### 🌐 4.2 Fluxo Interativo de Autenticação Web
Caso nenhuma sessão salva válida seja encontrada no chaveiro:
1. O CLI inicia automaticamente o seu navegador web padrão.
2. Você realiza o login e aprovação com sua conta Google autorizada.
3. O token retornado é gravado com criptografia segura no chaveiro nativo do Windows para sessões futuras.

---

## 🔍 5. Diagnóstico Rápido de Saúde do Ambiente

Para certificar que o ambiente está configurado corretamente:

```powershell
# 1. Verificar caminhos
Get-Command agy, antigravity | Select-Object Name, Source

# 2. Testar versão no PowerShell
agy --version

# 3. Testar execução via CMD
cmd.exe /c "antigravity --version"

# 4. Verificar se há atualizações pendentes
agy update
```
