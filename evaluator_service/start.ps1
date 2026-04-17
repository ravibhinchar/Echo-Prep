Write-Host "Starting Evaluator Service..." -ForegroundColor Green
Set-Location $PSScriptRoot
& .\venv\Scripts\Activate.ps1
python main.py

