<#
.SYNOPSIS
    Wrapper robusto para execução do Google Antigravity CLI (agy) em modo Headless.
.DESCRIPTION
    Executa prompts contra o agy de forma não-interativa, oferecendo parsing automático
    de saída JSON (ConvertFrom-Json), controle de formato, aplicação de JSON Schema e suporte a CI/CD.
.PARAMETER Prompt
    O prompt de instrução a ser enviado ao modelo.
.PARAMETER Format
    Formato da saída: 'text', 'json' ou 'stream-json'. Padrão: 'json'.
.PARAMETER JsonSchema
    String JSON ou caminho para arquivo .json definindo o schema de saída estruturada.
.PARAMETER Model
    Slug do modelo específico (ex: 'gemini-3.8-flash-high').
.PARAMETER Effort
    Esforço de raciocínio: 'low', 'medium', 'high'.
.PARAMETER Timeout
    Tempo máximo de espera (ex: '5m', '10m'). Padrão: '5m'.
.PARAMETER RawOutput
    Se definido, retorna a string bruta de stdout em vez de converter JSON em objeto.
.PARAMETER DangerouslySkipPermissions
    Se definido, adiciona a flag --dangerously-skip-permissions para pipelines automatizados.
.EXAMPLE
    .\run-agy-headless.ps1 -Prompt "Qual é a raiz quadrada de 144?"
.EXAMPLE
    .\run-agy-headless.ps1 -Prompt "Liste 3 frutas" -Format text
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Prompt,

    [Parameter(Mandatory = $false)]
    [ValidateSet('text', 'json', 'stream-json')]
    [string]$Format = 'json',

    [Parameter(Mandatory = $false)]
    [string]$JsonSchema = '',

    [Parameter(Mandatory = $false)]
    [string]$Model = '',

    [Parameter(Mandatory = $false)]
    [ValidateSet('low', 'medium', 'high')]
    [string]$Effort = '',

    [Parameter(Mandatory = $false)]
    [string]$Timeout = '5m',

    [Parameter(Mandatory = $false)]
    [switch]$RawOutput,

    [Parameter(Mandatory = $false)]
    [switch]$DangerouslySkipPermissions
)

$ErrorActionPreference = 'Stop'

# Localiza o binário do agy
$agyCmd = Get-Command agy -ErrorAction SilentlyContinue
if (-not $agyCmd) {
    $defaultPath = Join-Path $env:LOCALAPPDATA "agy\bin\agy.exe"
    if (Test-Path $defaultPath) {
        $agyPath = $defaultPath
    } else {
        Write-Error "O executável 'agy' não foi encontrado no PATH nem em $defaultPath."
        exit 1
    }
} else {
    $agyPath = $agyCmd.Source
}

# Monta os argumentos do CLI
$cliArgs = @("-p", $Prompt, "--output-format", $Format, "--print-timeout", $Timeout)

if ($JsonSchema -ne '') {
    $cliArgs += @("--json-schema", $JsonSchema)
}

if ($Model -ne '') {
    $cliArgs += @("--model", $Model)
}

if ($Effort -ne '') {
    $cliArgs += @("--effort", $Effort)
}

if ($DangerouslySkipPermissions) {
    $cliArgs += "--dangerously-skip-permissions"
}

Write-Verbose "Executando: & `"$agyPath`" $($cliArgs -join ' ')"

# Executa e captura stdout e stderr
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $agyPath
foreach ($arg in $cliArgs) {
    $psi.ArgumentList.Add($arg)
}
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$process = [System.Diagnostics.Process]::Start($psi)
$stdoutContent = $process.StandardOutput.ReadToEnd()
$stderrContent = $process.StandardError.ReadToEnd()
$process.WaitForExit()

if ($stderrContent) {
    [Console]::Error.Write($stderrContent)
}

if ($process.ExitCode -ne 0) {
    Write-Error "A execução do agy falhou com código de saída $($process.ExitCode)."
    if ($stdoutContent -and $Format -eq 'json') {
        try {
            $errObj = $stdoutContent | ConvertFrom-Json
            if ($errObj.error) {
                Write-Error "Detalhes do erro do modelo: $($errObj.error)"
            }
        } catch { }
    }
    exit $process.ExitCode
}

# Retorna a saída formatada
if ($RawOutput -or $Format -eq 'text') {
    return $stdoutContent
} elseif ($Format -eq 'json') {
    try {
        return ($stdoutContent | ConvertFrom-Json)
    } catch {
        Write-Warning "Falha ao converter saída JSON; retornando texto bruto."
        return $stdoutContent
    }
} else {
    # stream-json
    return $stdoutContent
}
