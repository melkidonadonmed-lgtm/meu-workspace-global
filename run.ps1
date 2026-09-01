<#
.SYNOPSIS
    Script Mestre de Automação do Repositório Global de Agentes (Windows PowerShell).
.DESCRIPTION
    Centraliza os comandos de desenvolvimento, servidores FastMCP, API Gateway e testes automatizados.
.EXAMPLE
    .\run.ps1 setup
    .\run.ps1 dev
    .\run.ps1 mcp -Transport sse
    .\run.ps1 test
#>

[CmdletBinding()]
param (
    [Parameter(Position = 0)]
    [ValidateSet("setup", "dev", "gateway", "mcp", "antigravity", "agent-go", "pcm", "keepdocs", "test", "lint", "clean", "help")]
    [string]$Command = "help",

    [Parameter()]
    [string]$Transport = "stdio",

    [Parameter()]
    [int]$Port = 8080
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param ([string]$Text)
    Write-Host "`n========================================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor White
    Write-Host "========================================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param ([string]$Text)
    Write-Host " [SUCCESS] $Text" -ForegroundColor Green
}

function Write-Info {
    param ([string]$Text)
    Write-Host " [INFO] $Text" -ForegroundColor Blue
}

function Write-WarningMsg {
    param ([string]$Text)
    Write-Host " [WARN] $Text" -ForegroundColor Yellow
}

# Garante que o PYTHONPATH aponte para a raiz
$env:PYTHONPATH = (Get-Location).Path

switch ($Command) {
    "setup" {
        Write-Header "Instalando Dependências do Ecossistema (Python, Node.js & Go)"
        
        # Copia .env.example para .env se não existir
        if (-not (Test-Path ".env")) {
            Copy-Item "configs/.env.example" ".env"
            Write-WarningMsg "Arquivo .env criado a partir de configs/.env.example. Adicione sua GEMINI_API_KEY!"
        }

        # Instalação do pacote Python em modo editável
        Write-Info "Instalando pacote Python em modo editável via pip..."
        python -m pip install -e ".[dev]"
        Write-Success "Dependências Python instaladas com sucesso!"

        # Configuração do agente Go
        if (Test-Path "projects/customer_issue_reviewer_go/go.mod") {
            Write-Info "Baixando dependências Go (google.golang.org/adk/v2)..."
            Push-Location "projects/customer_issue_reviewer_go"
            go mod tidy
            Pop-Location
            Write-Success "Módulo Go ADK v2 configurado!"
        }

        # Instalação do frontend Canvas IDE se existir
        if (Test-Path "projects/canvas_ide/package.json") {
            Write-Info "Instalando dependências Node.js do Canvas IDE..."
            Push-Location "projects/canvas_ide"
            npm install
            Pop-Location
            Write-Success "Frontend Canvas IDE configurado!"
        }

        # Instalação do app PCM (PrescMed) se existir
        if (Test-Path "projects/pcm/package.json") {
            Write-Info "Instalando dependências Node.js do PCM (PrescMed)..."
            Push-Location "projects/pcm"
            npm install
            Pop-Location
            Write-Success "Frontend PCM (PrescMed) configurado!"
        }

        # Instalação do app KeepDocs Workspace se existir
        if (Test-Path "projects/keepdocs-workspace/package.json") {
            Write-Info "Instalando dependências Node.js do KeepDocs Workspace..."
            Push-Location "projects/keepdocs-workspace"
            npm install
            Pop-Location
            Write-Success "KeepDocs Workspace configurado!"
        }
    }

    "dev" {
        Write-Header "Iniciando Ecossistema Completo de Desenvolvimento"
        Write-Info "Iniciando API Gateway (FastAPI) na porta 8000..."
        Write-Info "Iniciando Servidor FastMCP (SSE) na porta 8080..."
        
        Start-Job -ScriptBlock {
            $env:PYTHONPATH = (Get-Location).Path
            python -m mcp_servers.server --transport sse --port 8080
        } | Out-Null
        
        python -m uvicorn agents.api_gateway:app --host 0.0.0.0 --port 8000 --reload
    }

    "gateway" {
        Write-Header "Iniciando API Gateway (FastAPI) com SSE Streaming"
        python -m uvicorn agents.api_gateway:app --host 0.0.0.0 --port 8000 --reload
    }

    "mcp" {
        Write-Header "Iniciando Servidor FastMCP Unificado ($Transport)"
        if ($Transport -eq "sse") {
            python -m mcp_servers.server --transport sse --port $Port
        } else {
            python -m mcp_servers.server --transport stdio
        }
    }

    "antigravity" {
        Write-Header "Executando Google Antigravity Agent (Python SDK)"
        python -c "import asyncio; from agents.antigravity_bridge import AntigravityAgentBridge; bridge = AntigravityAgentBridge(); res = asyncio.run(bridge.chat('Status operacional e listagem do workspace')); print(res['response'])"
    }

    "agent-go" {
        Write-Header "Executando Customer Issue Reviewer Agent (Google ADK Go v2)"
        Push-Location "projects/customer_issue_reviewer_go"
        go run main.go
        Pop-Location
    }

    "pcm" {
        Write-Header "Iniciando PrescMed PCM (Vite Dev Server)"
        Push-Location "projects/pcm"
        npm run dev -- --open
        Pop-Location
    }

    "keepdocs" {
        Write-Header "Iniciando KeepDocs Workspace (Vite Dev Server)"
        Push-Location "projects/keepdocs-workspace"
        npm run dev -- --open
        Pop-Location
    }

    "test" {
        Write-Header "Executando Suíte Completa de Testes (Pytest + Go)"
        Write-Info "Rodando testes Python com pytest..."
        python -m pytest tests -v --tb=short
        
        if (Test-Path "projects/customer_issue_reviewer_go/go.mod") {
            Write-Info "Rodando testes Go ADK v2..."
            Push-Location "projects/customer_issue_reviewer_go"
            go test ./... -v
            Pop-Location
        }
        Write-Success "Todas as suítes de testes foram concluídas com sucesso!"
    }

    "lint" {
        Write-Header "Executando Validações de Qualidade de Código"
        Write-Info "Verificando com Ruff..."
        python -m ruff check .
        Write-Success "Verificação concluída sem erros!"
    }

    "clean" {
        Write-Header "Limpando Caches e Artefatos Temporários"
        Get-ChildItem -Path . -Include __pycache__, .pytest_cache, .mypy_cache -Recurse -Force | Remove-Item -Recurse -Force
        Write-Success "Caches removidos!"
    }

    Default {
        Write-Header "Ajuda e Comandos Disponíveis - run.ps1"
        Write-Host "Comandos:" -ForegroundColor Yellow
        Write-Host "  .\run.ps1 setup       - Instala dependências Python, Node.js e Go"
        Write-Host "  .\run.ps1 dev         - Executa API Gateway e Servidor FastMCP em paralelo"
        Write-Host "  .\run.ps1 gateway     - Executa somente o API Gateway FastAPI (porta 8000)"
        Write-Host "  .\run.ps1 mcp         - Executa o Servidor FastMCP (padrão: stdio)"
        Write-Host "  .\run.ps1 mcp -Transport sse - Executa Servidor FastMCP via SSE na porta 8080"
        Write-Host "  .\run.ps1 antigravity - Executa o agente do Google Antigravity SDK"
        Write-Host "  .\run.ps1 agent-go    - Executa o agente de chamados em Go (ADK v2)"
        Write-Host "  .\run.ps1 pcm         - Executa o frontend PrescMed PCM (Vite dev)"
        Write-Host "  .\run.ps1 keepdocs    - Executa o frontend KeepDocs Workspace (Vite dev)"
        Write-Host "  .\run.ps1 test        - Roda a suíte completa de testes (Python + Go)"
        Write-Host "  .\run.ps1 lint        - Valida formatação e qualidade com Ruff"
        Write-Host "  .\run.ps1 clean       - Remove caches e temporários Python`n"
    }
}
