[CmdletBinding()]
param (
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$Perfil = 'C:\Users\melki'
$Workspace = 'C:\Users\melki\meu-workspace-global'
$CanonicalProjetos = 'C:\Users\melki\Projetos'
$Quarentena = 'C:\Users\melki\_Arquivo\quarentena_brain_projetos'

if (-not (Test-Path $Quarentena)) {
    New-Item -ItemType Directory -Force -Path $Quarentena | Out-Null
}

function Write-Step([string]$msg) {
    Write-Host "`n[FAXINA] $msg" -ForegroundColor Cyan
}

function Write-Ok([string]$msg) {
    Write-Host "   OK: $msg" -ForegroundColor Green
}

$TotalBytesLiberados = 0

function Remover-Seguro([string]$caminho, [string]$motivo) {
    if (-not (Test-Path -LiteralPath $caminho)) {
        Write-Host "   [ausente] $caminho" -ForegroundColor DarkGray
        return
    }

    $size = 0
    try {
        $measure = Get-ChildItem -LiteralPath $caminho -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
        if ($measure -and $measure.Sum) { $size = $measure.Sum }
    } catch {}

    $script:TotalBytesLiberados += $size
    $mb = [math]::Round($size / 1MB, 1)

    if ($DryRun) {
        Write-Host "   [DryRun] Removeria: $caminho ($mb MB) -> $motivo" -ForegroundColor DarkYellow
    } else {
        try {
            Remove-Item -LiteralPath $caminho -Recurse -Force -ErrorAction Stop
            Write-Ok "Removido: $caminho ($mb MB) -> $motivo"
        } catch {
            Write-Warning "Falha ao remover ${caminho} - $($_.Exception.Message)"
        }
    }
}

function Mover-Quarentena([string]$origem, [string]$motivo) {
    if (-not (Test-Path -LiteralPath $origem)) {
        Write-Host "   [ausente] $origem" -ForegroundColor DarkGray
        return
    }

    $nome = Split-Path -Leaf $origem
    $destino = Join-Path $Quarentena $nome

    if ($DryRun) {
        Write-Host "   [DryRun] Moveria para quarentena: $origem -> $destino ($motivo)" -ForegroundColor DarkCyan
    } else {
        try {
            Move-Item -LiteralPath $origem -Destination $destino -Force -ErrorAction Stop
            Write-Ok "Movido para quarentena: $origem -> $destino"
        } catch {
            Write-Warning "Falha ao mover ${origem} - $($_.Exception.Message)"
        }
    }
}

Write-Step "1. Desduplicando projetos em meu-workspace-global\projects (preservando C:\Users\melki\Projetos)..."
$ProjetosDuplicados = @('pcm', 'canvas_ide', 'keepdocs-workspace', 'WAOE', 'remix-prescmed-new')
foreach ($p in $ProjetosDuplicados) {
    $caminhoWs = Join-Path "$Workspace\projects" $p
    $caminhoCan = Join-Path $CanonicalProjetos $p
    if (Test-Path $caminhoCan) {
        Remover-Seguro $caminhoWs "Copia redundante; versao canonica preservada em $caminhoCan"
    } else {
        Write-Warning "ATENCAO: Nao removendo $caminhoWs pois $caminhoCan nao foi localizado!"
    }
}

Write-Step "2. Removendo ambiente virtual orfao da raiz do usuario..."
Remover-Seguro (Join-Path $Perfil '.venv') "Venv criado por engano com Python Store na raiz do perfil"

Write-Step "3. Removendo instalacoes legadas paradas..."
Remover-Seguro (Join-Path $Perfil '.antigravity-ide') "Instalacao congelada de 15/08 (ativa em AppData\Local\Programs\Antigravity IDE)"
Remover-Seguro (Join-Path $Perfil 'free-vscode-csharp') "Ambiente de testes C# de 11/08 descontinuado"
Remover-Seguro (Join-Path $Perfil 'vscode-antigravity-cockpit') "Ambiente de testes de cockpit descontinuado"

Write-Step "4. Removendo residuos legados de Kimi / OpenClaw..."
Remover-Seguro (Join-Path $Perfil '.kimi') "Pasta legada (CLI ativa e .kimi-code)"
Remover-Seguro (Join-Path $Perfil '.kimi-work') "Daemon legado do Kimi"
Remover-Seguro (Join-Path $Perfil '.kimi-webbridge') "Daemon legado de webbridge"
Remover-Seguro (Join-Path $Perfil '.kimi_openclaw') "Residuo de integracao OpenClaw"
Remover-Seguro (Join-Path $Perfil '.snowflake') "Pasta vazia residual de scaffold"

Write-Step "5. Removendo arquivos de exemplo soltos em C:\Users\melki\projetos..."
Remover-Seguro (Join-Path $CanonicalProjetos 'Another example txt file.txt') "Arquivo de teste solto"
Remover-Seguro (Join-Path $CanonicalProjetos 'Example txt file.txt') "Arquivo de teste solto"

Write-Step "6. Movendo copias mortas/sem git de Brain\projetos para quarentena..."
Mover-Quarentena (Join-Path "$Perfil\Brain\projetos" 'Kimi_Agent_PresCMed原型') "Copia antiga sem git"
Mover-Quarentena (Join-Path "$Perfil\Brain\projetos" 'PresCMed v2') "Pasta vazia sem arquivos (0 MB)"
Mover-Quarentena (Join-Path "$Perfil\Brain\projetos" 'prototype-orchestrator-bigquery') "Prototipo antigo sem git"

$TotalMB = [math]::Round($TotalBytesLiberados / 1MB, 1)
$TotalGB = [math]::Round($TotalBytesLiberados / 1GB, 2)
Write-Step "FAXINA CONCLUIDA! Espaco total liberado/processado: $TotalMB MB ($TotalGB GB)."
