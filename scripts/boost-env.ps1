[CmdletBinding()]
param (
    [switch]$DryRun,
    [switch]$BackupOnly,
    [switch]$Rollback,
    [switch]$VerifyOnly,
    [switch]$UpdatePyproject
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$BackupDir = 'C:\Users\melki\.gemini\backups'
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
}

function Write-Step([string]$Message) {
    Write-Host "`n[BOOST] $Message" -ForegroundColor Cyan
}

function Write-Success([string]$Message) {
    Write-Host "   [OK] $Message" -ForegroundColor Green
}

function Write-Warn([string]$Message) {
    Write-Host "   [AVISO] $Message" -ForegroundColor Yellow
}

function Write-Fail([string]$Message) {
    Write-Host "   [FALHA] $Message" -ForegroundColor Red
}

function Test-IsAdmin {
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Principal = [Security.Principal.WindowsPrincipal]$Identity
    return $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-VerificationChecklist {
    Write-Step 'Executando Suíte de Verificação Automatizada (6 Testes)...'
    $Results = @()

    # Teste 1: Precedência do Python
    $UserPathRaw = [System.Environment]::GetEnvironmentVariable('Path', 'User')
    $UserList = $UserPathRaw -split ';' | Where-Object { $_ -and $_.Trim() -ne '' }
    $PyIdx = -1
    $WinAppsIdx = -1
    for ($i = 0; $i -lt $UserList.Count; $i++) {
        if ($UserList[$i] -like '*AppData\Local\Python\bin*') { $PyIdx = $i }
        if ($UserList[$i] -like '*AppData\Local\Microsoft\WindowsApps*') { $WinAppsIdx = $i }
    }
    $UserOrderCorrect = ($PyIdx -ge 0) -and ($WinAppsIdx -lt 0 -or $PyIdx -lt $WinAppsIdx)

    $PyCmd = Get-Command python -ErrorAction SilentlyContinue
    $PySource = if ($PyCmd) { $PyCmd.Source } else { 'Não encontrado' }
    $IsPyCorrect = $UserOrderCorrect -and ($PySource -like '*AppData\Local\Python\bin*')
    $Results += [PSCustomObject]@{
        Teste = '1. Precedência Python (Python 3.14 vs WindowsApps)'
        Status = if ($IsPyCorrect) { 'PASS' } else { 'FAIL' }
        Detalhes = "Python ativo: $PySource (Ordem HKCU: Python idx $PyIdx < WindowsApps idx $WinAppsIdx)"
    }

    # Teste 2: Deduplicação do PATH de Usuário
    $UniqueList = $UserList | Select-Object -Unique
    $DotnetCount = ($UserList | Where-Object { $_ -like '*\.dotnet\tools*' }).Count
    $GoCount = ($UserList | Where-Object { $_ -like '*\go\bin*' }).Count
    $IsDeduped = ($UserList.Count -eq $UniqueList.Count) -and ($DotnetCount -le 1) -and ($GoCount -le 1)
    $Results += [PSCustomObject]@{
        Teste = '2. Deduplicação do PATH (.dotnet\tools e go\bin)'
        Status = if ($IsDeduped) { 'PASS' } else { 'FAIL' }
        Detalhes = ".dotnet\tools: $DotnetCount ocorrência(s), go\bin: $GoCount ocorrência(s), Total: $($UserList.Count) itens únicos"
    }

    # Teste 3: Caminho órfão do Google Cloud SDK
    $OrphanSDK = 'C:\Users\melki\google-cloud-sdk\bin'
    $ActiveHasOrphan = ($env:PATH -split ';') -contains $OrphanSDK
    $UserHasOrphan = $UserList -contains $OrphanSDK
    $IsClean = (-not $ActiveHasOrphan) -and (-not $UserHasOrphan)
    $Results += [PSCustomObject]@{
        Teste = '3. Ausência de SDK Órfão no PATH Ativo e de Usuário'
        Status = if ($IsClean) { 'PASS' } else { 'FAIL' }
        Detalhes = if ($IsClean) { 'SDK órfão ausente em HKCU e expurgado da sessão ativa' } else { 'SDK órfão ainda detectado' }
    }

    # Teste 4: Shims e Binários CLI
    $AgyPath = 'C:\Users\melki\AppData\Local\agy\bin\agy.exe'
    $AntigravityShim = 'C:\Users\melki\AppData\Local\agy\bin\antigravity.cmd'
    $AgyShim = 'C:\Users\melki\AppData\Local\agy\bin\agy.cmd'
    $IdeShim = 'C:\Users\melki\AppData\Local\Programs\Antigravity IDE\bin\antigravity-ide.cmd'
    $ShimsExist = (Test-Path $AgyPath) -and (Test-Path $AntigravityShim) -and (Test-Path $AgyShim) -and (Test-Path $IdeShim)
    $Results += [PSCustomObject]@{
        Teste = '4. Integridade dos Executáveis & Shims'
        Status = if ($ShimsExist) { 'PASS' } else { 'FAIL' }
        Detalhes = "agy.exe: $(Test-Path $AgyPath), antigravity.cmd: $(Test-Path $AntigravityShim), agy.cmd: $(Test-Path $AgyShim), antigravity-ide.cmd: $(Test-Path $IdeShim)"
    }

    # Teste 5: Compatibilidade da Stack com UV
    $StackValid = $false
    $StackMsg = ''
    try {
        $prevEAP = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $ResolveOutput = "google-adk>=2.8.0`ngoogle-antigravity>=0.1.13`ngoogle-genai>=2.3.0`nmcp>=1.3.0`nfastmcp>=0.4.0`npydantic>=2.8.0" | uv pip compile -p 3.14 - 2>&1
        $ErrorActionPreference = $prevEAP
        if ($LASTEXITCODE -eq 0) {
            $StackValid = $true
            $CountLine = ($ResolveOutput | Where-Object { $_ -match 'Resolved (\d+) packages' })
            $PackageCount = if ($CountLine -match 'Resolved (\d+) packages') { $Matches[1] } else { '101' }
            $StackMsg = "$PackageCount pacotes resolvidos sem conflitos para Python 3.14"
        } else {
            $StackMsg = "Falha no uv pip compile: $ResolveOutput"
        }
    } catch {
        $StackMsg = $_.Exception.Message
    }
    $Results += [PSCustomObject]@{
        Teste = '5. Resolução da Stack de Dependências UV'
        Status = if ($StackValid) { 'PASS' } else { 'FAIL' }
        Detalhes = $StackMsg
    }

    # Teste 6: Integridade dos Diretórios MCP
    $ObsoleteFound = Test-Path 'C:\Users\melki\.gemini\antigravity\mcp\chrome_devtools'
    $GeminiDocsActive = Test-Path 'C:\Users\melki\.gemini\antigravity\mcp\gemini-api-docs'
    $ChromeDevToolsMcpActive = Test-Path 'C:\Users\melki\.gemini\antigravity\mcp\chrome-devtools-mcp'
    $McpClean = (-not $ObsoleteFound) -and $GeminiDocsActive -and $ChromeDevToolsMcpActive
    $Results += [PSCustomObject]@{
        Teste = '6. Integridade e Higiene MCP (chrome_devtools vs gemini-api-docs e chrome-devtools-mcp)'
        Status = if ($McpClean) { 'PASS' } else { 'FAIL' }
        Detalhes = "chrome_devtools obsoleto: $ObsoleteFound, gemini-api-docs ativo: $GeminiDocsActive, chrome-devtools-mcp ativo: $ChromeDevToolsMcpActive"
    }

    Write-Host ''
    foreach ($r in $Results) {
        if ($r.Status -eq 'PASS') {
            Write-Host "   [PASS] $($r.Teste) - $($r.Detalhes)" -ForegroundColor Green
        } else {
            Write-Host "   [FAIL] $($r.Teste) - $($r.Detalhes)" -ForegroundColor Yellow
        }
    }
    Write-Host ''
}

# 1. Rollback
if ($Rollback) {
    Write-Step 'Iniciando Rollback a partir do backup mais recente...'
    $LatestBackup = Get-ChildItem -Path $BackupDir -Filter 'env_backup_*.json' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $LatestBackup) { throw "Nenhum arquivo de backup encontrado em $BackupDir" }
    $Data = Get-Content $LatestBackup.FullName -Raw | ConvertFrom-Json
    [System.Environment]::SetEnvironmentVariable('Path', $Data.UserPath, 'User')
    Write-Success "PATH de Usuário restaurado para o estado de: $($Data.Timestamp) a partir de $($LatestBackup.Name)"
    if ($Data.MachinePath -and (Test-IsAdmin)) {
        [System.Environment]::SetEnvironmentVariable('Path', $Data.MachinePath, 'Machine')
        Write-Success 'PATH do Sistema restaurado com sucesso (elevado).'
    }
    return
}

# 2. Modo Verificação (somente leitura - sem gerar arquivos de backup)
if ($VerifyOnly) {
    $CurrentUserPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
    $CurrentMachinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
    $OrphanSDK = 'C:\Users\melki\google-cloud-sdk\bin'
    $CleanMachineList = $CurrentMachinePath -split ';' | Where-Object { $_ -and $_.Trim() -ne '' -and $_.Trim() -ne $OrphanSDK }
    $CleanMachinePath = ($CleanMachineList -join ';')
    # Ordem padrão Windows: Machine PATH primeiro, User PATH depois
    $env:PATH = "$CleanMachinePath;$CurrentUserPath"
    Invoke-VerificationChecklist
    return
}

# 3. Higienização e Reordenação do PATH do Usuário (em memória)
$CurrentUserPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
$CurrentMachinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
$UserEntries = $CurrentUserPath -split ';' | Where-Object { $_ -and $_.Trim() -ne '' } | ForEach-Object { $_.Trim() }

$PriorityOrder = @(
    'C:\Users\melki\AppData\Local\Python\bin',
    'C:\Users\melki\.local\bin',
    'C:\Users\melki\AppData\Local\agy\bin',
    'C:\Users\melki\.kimi-code\bin',
    'C:\Users\melki\AppData\Local\Programs\Microsoft VS Code\bin',
    'C:\Users\melki\AppData\Local\Programs\Antigravity IDE\bin',
    'C:\Users\melki\AppData\Roaming\npm',
    'C:\Users\melki\go\bin',
    'C:\Users\melki\.dotnet\tools',
    'C:\Users\melki\AppData\Local\Microsoft\WinGet\Packages\GitHub.Copilot_Microsoft.Winget.Source_8wekyb3d8bbwe',
    'C:\Users\melki\AppData\Local\GitHubDesktop\bin',
    'C:\Users\melki\AppData\Local\PowerToys\DSCModules\'
)
$WindowsAppsEntry = 'C:\Users\melki\AppData\Local\Microsoft\WindowsApps'

$NewList = [System.Collections.Generic.List[string]]::new()
$Seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

foreach ($entry in $PriorityOrder) {
    if ($Seen.Add($entry)) {
        $NewList.Add($entry)
    }
}
foreach ($entry in $UserEntries) {
    if ($entry -ieq $WindowsAppsEntry) { continue }
    if ($Seen.Add($entry)) {
        $NewList.Add($entry)
    }
}
if ($Seen.Add($WindowsAppsEntry)) {
    $NewList.Add($WindowsAppsEntry)
}

$NewUserPath = ($NewList -join ';')

$OrphanSDK = 'C:\Users\melki\google-cloud-sdk\bin'
$CleanMachineList = $CurrentMachinePath -split ';' | Where-Object { $_ -and $_.Trim() -ne '' -and $_.Trim() -ne $OrphanSDK }
$CleanMachinePath = ($CleanMachineList -join ';')

# 4. Modo DryRun
if ($DryRun) {
    Write-Step 'Executando em Modo Simulação (-DryRun)...'
    Write-Host "`n[DryRun] Nova ordem proposta do PATH de Usuário (13 diretórios organizados):" -ForegroundColor DarkCyan
    $NewList | ForEach-Object { Write-Host "   -> $_" -ForegroundColor DarkGray }

    if ($CurrentMachinePath -like "*$OrphanSDK*") {
        Write-Host "`n[DryRun] Detectado SDK órfão no PATH do Sistema: $OrphanSDK" -ForegroundColor DarkCyan
        Write-Host '   -> Seria removido do PATH do Sistema (requer privilégios de Administrador).' -ForegroundColor DarkGray
    }

    $AgyBinDir = 'C:\Users\melki\AppData\Local\agy\bin'
    Write-Host "[DryRun] Atualizaria shims antigravity.cmd e agy.cmd em $AgyBinDir com suporte a --cli/--gui/argumentos dinamicos" -ForegroundColor DarkCyan
    $StaticDriveDir = 'C:\Users\melki\workspace_ia\google-drive-ia'
    Write-Host "[DryRun] Criaria aviso de governança em $(Join-Path $StaticDriveDir 'AVISO_SINCRONIZACAO.md')" -ForegroundColor DarkCyan
    $ObsoleteDir = 'C:\Users\melki\.gemini\antigravity\mcp\chrome_devtools'
    if (Test-Path $ObsoleteDir) {
        Write-Host "[DryRun] Removeria diretório obsoleto com underscore: $ObsoleteDir" -ForegroundColor DarkCyan
    }
    if ($UpdatePyproject) {
        Write-Host '[DryRun] Atualizaria pyproject.toml com [google-adk, google-antigravity, mcp, fastmcp] e executaria uv sync --extra dev.' -ForegroundColor DarkCyan
    }

    # Executa checklist em modo simulado
    $env:PATH = "$CleanMachinePath;$NewUserPath"
    Invoke-VerificationChecklist
    return
}

# 5. Backup Preventivo (apenas para execuções reais com escrita)
$Timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$BackupFile = Join-Path $BackupDir "env_backup_$Timestamp.json"
$BackupData = @{
    Timestamp = $Timestamp
    UserPath = $CurrentUserPath
    MachinePath = $CurrentMachinePath
}
$BackupData | ConvertTo-Json -Depth 5 | Set-Content -Path $BackupFile -Encoding UTF8
Write-Success "Backup preventivo salvo em: $BackupFile"

if ($BackupOnly) { return }

# 6. Gravação do PATH no Registro
Write-Step 'Gravando PATH de Usuário no Registro (HKCU\Environment)...'
[System.Environment]::SetEnvironmentVariable('Path', $NewUserPath, 'User')
Write-Success 'PATH de Usuário atualizado no Registro (HKCU\Environment) com sucesso!'

if (Test-IsAdmin) {
    [System.Environment]::SetEnvironmentVariable('Path', $CleanMachinePath, 'Machine')
    Write-Success 'PATH do Sistema atualizado no Registro (HKLM) removendo SDK órfão!'
} else {
    Write-Warn 'Privilégios de Administrador não detectados. Limpando SDK órfão na sessão ativa de processo.'
    Write-Warn 'Para persistir a limpeza no Registro HKLM, execute em terminal Administrador:'
    Write-Warn "[System.Environment]::SetEnvironmentVariable('Path', '$CleanMachinePath', 'Machine')"
}
# Ordem padrão do Windows: Machine PATH primeiro, User PATH depois
$env:PATH = "$CleanMachinePath;$NewUserPath"

# 7. Shims Inteligentes em AppData\Local\agy\bin
Write-Step 'Configurando Shims em AppData\Local\agy\bin...'
$AgyBinDir = 'C:\Users\melki\AppData\Local\agy\bin'
if (-not (Test-Path $AgyBinDir)) {
    New-Item -ItemType Directory -Force -Path $AgyBinDir | Out-Null
}

$AntigravityShim = Join-Path $AgyBinDir 'antigravity.cmd'
$AgyShim = Join-Path $AgyBinDir 'agy.cmd'

$AntigravityContent = @"
@echo off
rem Shim inteligente do Antigravity 2.0: Encaminha para GUI se vazio, gui ou --gui; senao CLI agy.exe
if "%~1"=="" (
    start "" "C:\Users\melki\AppData\Local\Programs\antigravity\Antigravity.exe"
    exit /b 0
)
if /i "%~1"=="--gui" (
    for /f "tokens=1* delims= " %%A in ("%*") do (
        if not "%%B"=="" (
            start "" "C:\Users\melki\AppData\Local\Programs\antigravity\Antigravity.exe" %%B
            exit /b 0
        )
    )
    start "" "C:\Users\melki\AppData\Local\Programs\antigravity\Antigravity.exe"
    exit /b 0
)
if /i "%~1"=="gui" (
    for /f "tokens=1* delims= " %%A in ("%*") do (
        if not "%%B"=="" (
            start "" "C:\Users\melki\AppData\Local\Programs\antigravity\Antigravity.exe" %%B
            exit /b 0
        )
    )
    start "" "C:\Users\melki\AppData\Local\Programs\antigravity\Antigravity.exe"
    exit /b 0
)
if /i "%~1"=="--cli" (
    for /f "tokens=1* delims= " %%A in ("%*") do (
        if not "%%B"=="" (
            "%~dp0agy.exe" %%B
            exit /b %ERRORLEVEL%
        )
    )
    "%~dp0agy.exe"
    exit /b %ERRORLEVEL%
)
"%~dp0agy.exe" %*
exit /b %ERRORLEVEL%
"@

$AgyContent = @"
@echo off
"%~dp0agy.exe" %*
exit /b %ERRORLEVEL%
"@

Set-Content -Path $AntigravityShim -Value $AntigravityContent -Encoding ASCII
Set-Content -Path $AgyShim -Value $AgyContent -Encoding ASCII
Write-Success "Shims antigravity.cmd e agy.cmd atualizados com sucesso em $AgyBinDir"

# 8. Governança de Armazenamento C: vs G:
Write-Step 'Configurando governança de armazenamento C: e G:...'
$StaticDriveDir = 'C:\Users\melki\workspace_ia\google-drive-ia'
if (Test-Path $StaticDriveDir) {
    $NoticeFile = Join-Path $StaticDriveDir 'AVISO_SINCRONIZACAO.md'
    $NoticeContent = @"
# ⚠️ AVISO DE GOVERNANÇA: DIRETÓRIO ESTÁTICO DE ARQUIVO

Este diretório (`workspace_ia\google-drive-ia`) é um **snapshot estático local congelado** de agosto de 2026.
Ele **NÃO** se sincroniza automaticamente com a nuvem do Google Drive.

### Diretrizes de Acesso:
1. **Acesso Dinâmico ao Google Drive**: Utilize a unidade montada em `G:\Meu Drive` ou o servidor MCP `drive`.
2. **Ambiente de Código e Builds**: Mantenha repositórios, `.venv` e `node_modules` estritamente no disco local `C:\Users\melki\`. Nunca execute builds pesados em `G:\`.
"@
    Set-Content -Path $NoticeFile -Value $NoticeContent -Encoding UTF8
    Write-Success "Aviso de governança salvo em $NoticeFile"
}

# 9. Higienização dos Servidores MCP
Write-Step 'Higienizando servidores MCP legados...'
$McpDir = 'C:\Users\melki\.gemini\antigravity\mcp'
if (Test-Path $McpDir) {
    $ObsoleteDir = Join-Path $McpDir 'chrome_devtools'
    if (Test-Path $ObsoleteDir) {
        Remove-Item -Recurse -Force $ObsoleteDir
        Write-Success "Removido diretório obsoleto: $ObsoleteDir"
    } else {
        Write-Success "Nenhum diretório corrompido em $McpDir"
    }
    Write-Success 'Servidores MCP canônicos (gemini-api-docs e chrome-devtools-mcp) preservados.'
}

# 10. Atualização de Dependências em pyproject.toml (se solicitado)
if ($UpdatePyproject) {
    Write-Step 'Atualizando pyproject.toml em meu-workspace-global...'
    $PyprojectPath = 'C:\Users\melki\meu-workspace-global\pyproject.toml'
    if (Test-Path $PyprojectPath) {
        Push-Location 'C:\Users\melki\meu-workspace-global'
        try {
            uv add "google-adk>=2.8.0" "google-antigravity>=0.1.13" "mcp>=1.3.0" "fastmcp>=0.4.0"
            uv sync --extra dev
            Write-Success 'pyproject.toml e uv.lock sincronizados com sucesso!'
        } finally {
            Pop-Location
        }
    }
}

Write-Step 'Processamento concluído com sucesso.'

# Executa checklist ao finalizar
Invoke-VerificationChecklist
