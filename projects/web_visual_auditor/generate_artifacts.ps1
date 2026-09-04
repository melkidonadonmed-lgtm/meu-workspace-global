# Script PowerShell para geração física dos artefatos PNG
$ErrorActionPreference = "Stop"
Write-Host "Iniciando geração de artefatos PNG..." -ForegroundColor Cyan
uv run python generate_diff_artifacts.py
Write-Host "Concluído com sucesso!" -ForegroundColor Green
