$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot 'backend'
$pythonCommand = if (Test-Path (Join-Path $backendRoot '.venv\Scripts\python.exe')) { (Join-Path $backendRoot '.venv\Scripts\python.exe') } else { 'py -3.11' }

Start-Process powershell -ArgumentList @(
  '-NoExit',
  '-ExecutionPolicy', 'Bypass',
  '-Command', "Set-Location -LiteralPath '$backendRoot'; `$env:PYTHONPATH = (Get-Location).Path; $pythonCommand -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
)

