[CmdletBinding()]
param ([switch]$DryRun)

$ErrorActionPreference = 'Stop'
$Perfil = 'C:\Users\melki'
$Workspace = 'C:\Users\melki\meu-workspace-global'

$AlvosLimpeza = @(
    @{ Path = "$Perfil\AppData\Local\npm-cache\_logs"; Desc = "Logs de depuracao do npm" },
    @{ Path = "$Perfil\.cache\codex-runtimes"; Desc = "Runtimes recriaveis do Codex CLI (1.33 GB)" },
    @{ Path = "$Perfil\.cache\puppeteer"; Desc = "Chromium de testes do Puppeteer (696 MB)" },
    @{ Path = "$Workspace\.pytest_cache"; Desc = "Cache de execucao do Pytest" },
    @{ Path = "$Workspace\.ruff_cache"; Desc = "Cache de linter do Ruff" },
    @{ Path = "$Perfil\.ghcp-appmod\logs"; Desc = "Logs legados do AppMod" },
    @{ Path = "$Perfil\.local\share\opencode\log"; Desc = "Logs legados do OpenCode" }
)

Write-Host "`n[LIMPEZA] Iniciando higienizacao de logs e caches recriaveis..." -ForegroundColor Cyan

$TotalBytesLiberados = 0

foreach ($item in $AlvosLimpeza) {
    if (Test-Path -LiteralPath $item.Path) {
        $size = 0
        try {
            $measure = Get-ChildItem -LiteralPath $item.Path -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
            if ($measure -and $measure.Sum) { $size = $measure.Sum }
        } catch {}

        $TotalBytesLiberados += $size
        $mb = [math]::Round($size / 1MB, 1)

        if ($DryRun) {
            Write-Host "   [DryRun] Limparia: $($item.Path) ($mb MB) -> $($item.Desc)" -ForegroundColor Yellow
        } else {
            try {
                Remove-Item -LiteralPath $item.Path -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "   [OK] Limpo: $($item.Path) ($mb MB) -> $($item.Desc)" -ForegroundColor Green
            } catch {
                Write-Warning "Falha ao limpar $($item.Path): $($_.Exception.Message)"
            }
        }
    } else {
        Write-Host "   [ausente] $($item.Path)" -ForegroundColor DarkGray
    }
}

$TotalMB = [math]::Round($TotalBytesLiberados / 1MB, 1)
$TotalGB = [math]::Round($TotalBytesLiberados / 1GB, 2)
Write-Host "`n[LIMPEZA] Concluida! Espaco liberado em logs e caches: $TotalMB MB ($TotalGB GB).`n" -ForegroundColor Cyan
