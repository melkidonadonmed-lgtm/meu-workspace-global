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
    [ValidateSet("setup", "dev", "gateway", "mcp", "test", "lint", "clean", "help")]
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
        Write-Header "Instalando Dependências do Ecossistema (Python & Node.js)"
        
        # Copia .env.example para .env se não existir
        if (-not (Test-Path ".env")) {
            Copy-Item "configs/.env.example" ".env"
            Write-WarningMsg "Arquivo .env criado a partir de configs/.env.example. Adicione sua GEMINI_API_KEY!"
        }

        # Instalação do pacote Python em modo editável
        Write-Info "Instalando pacote Python em modo editável via pip..."
        pip install -e ".[dev]"
        Write-Success "Dependências Python instaladas com sucesso!"

        # Instalação do frontend se existir
        if (Test-Path "projects/canvas_ide/package.json") {
            Write-Info "Instalando dependências Node.js do Canvas IDE..."
            Push-Location "projects/canvas_ide"
            npm install
            Pop-Location
            Write-Success "Frontend Canvas IDE configurado!"
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

    "test" {
        Write-Header "Executando Suíte de Testes Automatizados (pytest)"
        pytest tests -v --tb=short
        Write-Success "Suíte de testes finalizada com sucesso!"
    }

    "lint" {
        Write-Header "Executando Validações de Qualidade de Código"
        Write-Info "Verificando com Ruff..."
        ruff check .
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
        Write-Host "  .\run.ps1 setup       - Instala dependências Python e Node.js em modo editável"
        Write-Host "  .\run.ps1 dev         - Executa API Gateway e Servidor FastMCP em paralelo"
        Write-Host "  .\run.ps1 gateway     - Executa somente o API Gateway FastAPI (porta 8000)"
        Write-Host "  .\run.ps1 mcp         - Executa o Servidor FastMCP (padrão: stdio)"
        Write-Host "  .\run.ps1 mcp -Transport sse - Executa Servidor FastMCP via SSE na porta 8080"
        Write-Host "  .\run.ps1 test        - Roda os testes unitários e de integração com pytest"
        Write-Host "  .\run.ps1 lint        - Valida formatação e qualidade com Ruff"
        Write-Host "  .\run.ps1 clean       - Remove caches e temporários Python`n"
    }
}
