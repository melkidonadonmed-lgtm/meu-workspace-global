<#
.SYNOPSIS
    Script de auditoria e diagnóstico de ambiente Windows para o Google Antigravity CLI (agy).
.DESCRIPTION
    Verifica a presença dos binários em %LOCALAPPDATA%\agy\bin, configuração de PATH,
    execução via PowerShell e CMD, e conectividade de autenticação.
.PARAMETER Fix
    Se especificado, tenta auto-reparar o PATH do usuário caso esteja ausente.
.EXAMPLE
    .\check-windows-environment.ps1
.EXAMPLE
    .\check-windows-environment.ps1 -Fix
#>

[CmdletBinding()]
param(
    [switch]$Fix
)

$ErrorActionPreference = 'Continue'

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Diagnóstico de Ambiente Windows - Antigravity CLI (agy) " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$expectedBinDir = Join-Path $env:LOCALAPPDATA "agy\bin"
$agyExePath = Join-Path $expectedBinDir "agy.exe"
$antigravityCmdPath = Join-Path $expectedBinDir "antigravity.cmd"

$allOk = $true

# 1. Checagem do Diretório de Binários
Write-Host "`n[1/5] Verificando diretório de instalação..." -NoNewline
if (Test-Path $expectedBinDir) {
    Write-Host " [OK]" -ForegroundColor Green
    Write-Host "      Caminho: $expectedBinDir" -ForegroundColor DarkGray
} else {
    Write-Host " [FALHA]" -ForegroundColor Red
    Write-Host "      Diretório não encontrado: $expectedBinDir" -ForegroundColor Yellow
    $allOk = $false
}

# 2. Checagem de Executáveis
Write-Host "`n[2/5] Verificando binários instalados..."
$hasAgy = Test-Path $agyExePath
$hasCmd = Test-Path $antigravityCmdPath

if ($hasAgy) {
    Write-Host "      - agy.exe: [OK] ($agyExePath)" -ForegroundColor Green
} else {
    Write-Host "      - agy.exe: [FALHA] (Ausente)" -ForegroundColor Red
    $allOk = $false
}

if ($hasCmd) {
    Write-Host "      - antigravity.cmd: [OK] ($antigravityCmdPath)" -ForegroundColor Green
} else {
    Write-Host "      - antigravity.cmd: [FALHA] (Ausente)" -ForegroundColor Red
    $allOk = $false
}

# 3. Checagem da Variável de Ambiente PATH
Write-Host "`n[3/5] Verificando configuração da variável PATH..."
$userPath = [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::User)
$currentPath = $env:PATH

$inUserPath = $userPath -split ';' | Where-Object { $_.TrimEnd('\') -eq $expectedBinDir.TrimEnd('\') }
$inCurrentPath = $currentPath -split ';' | Where-Object { $_.TrimEnd('\') -eq $expectedBinDir.TrimEnd('\') }

if ($inCurrentPath) {
    Write-Host "      - PATH da sessão atual: [OK]" -ForegroundColor Green
} else {
    Write-Host "      - PATH da sessão atual: [FALHA] (Não localizado)" -ForegroundColor Yellow
    $allOk = $false
}

if ($inUserPath) {
    Write-Host "      - PATH persistente do usuário: [OK]" -ForegroundColor Green
} else {
    Write-Host "      - PATH persistente do usuário: [AVISO] (Não presente no registro de usuário)" -ForegroundColor Yellow
    if ($Fix) {
        Write-Host "      -> Aplicando correção (-Fix)..." -ForegroundColor Cyan
        $newUserPath = "$userPath;$expectedBinDir"
        [System.Environment]::SetEnvironmentVariable("PATH", $newUserPath, [System.EnvironmentVariableTarget]::User)
        Write-Host "      -> $expectedBinDir adicionado ao PATH de usuário com sucesso!" -ForegroundColor Green
    }
}

# 4. Teste de Execução Funcional (PowerShell e CMD)
Write-Host "`n[4/5] Testando execução funcional..."
try {
    $psVersion = & $agyExePath --version 2>&1
    Write-Host "      - Execução PowerShell (agy --version): [OK] (Versão: $psVersion)" -ForegroundColor Green
} catch {
    Write-Host "      - Execução PowerShell falhou: $_" -ForegroundColor Red
    $allOk = $false
}

try {
    $cmdOutput = cmd.exe /c "$antigravityCmdPath --version" 2>&1
    Write-Host "      - Execução CMD (antigravity --version): [OK] (Versão: $cmdOutput)" -ForegroundColor Green
} catch {
    Write-Host "      - Execução CMD falhou: $_" -ForegroundColor Red
    $allOk = $false
}

# 5. Verificação de Autenticação / Conectividade
Write-Host "`n[5/5] Testando resposta rápida do agente (Silent Sign-In)..."
try {
    $authCheck = & $agyExePath -p "Diga apenas 'OK'" --print-timeout 10s --output-format text 2>$null
    if ($authCheck -match "OK") {
        Write-Host "      - Autenticação e Chaveiro (CredMan): [OK] (Conectado silenciosamente)" -ForegroundColor Green
    } else {
        Write-Host "      - Resposta recebida: $authCheck" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "      - Verificação de autenticação: [AVISO] ($_)" -ForegroundColor Yellow
}

Write-Host "`n----------------------------------------------------------"
if ($allOk) {
    Write-Host "[OK] Diagnóstico concluído: O ambiente Windows está 100% íntegro e operacional!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[AVISO] Diagnóstico concluído com ressalvas. Verifique os avisos acima." -ForegroundColor Yellow
    exit 1
}
