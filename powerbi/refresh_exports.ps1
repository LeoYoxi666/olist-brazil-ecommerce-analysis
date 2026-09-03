$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw ".venv not found. Create it and install requirements.txt first."
}

Push-Location $projectRoot
try {
    & $pythonPath "scripts\run_pipeline.py"
    if ($LASTEXITCODE -ne 0) { throw "Data pipeline failed." }

    & $pythonPath "scripts\run_analysis.py"
    if ($LASTEXITCODE -ne 0) { throw "Analysis workflow failed." }

    & $pythonPath "scripts\export_powerbi.py"
    if ($LASTEXITCODE -ne 0) { throw "Power BI export failed." }
}
finally {
    Pop-Location
}

Write-Host "Power BI exports refreshed. Select Refresh in Power BI Desktop."
