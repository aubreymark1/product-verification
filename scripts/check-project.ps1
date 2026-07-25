$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot 'frontend'
$backendRoot = Join-Path $repoRoot 'backend'
$backendPython = if (Test-Path (Join-Path $backendRoot '.venv\Scripts\python.exe')) { (Join-Path $backendRoot '.venv\Scripts\python.exe') } else { 'python' }

Write-Host '== Frontend type check =='
Push-Location $frontendRoot
npm run type-check
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Write-Host '== Frontend build =='
npm run build
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Pop-Location

Write-Host '== Backend import check =='
$env:PYTHONPATH = $backendRoot
Push-Location $backendRoot
& $backendPython -c "from app.main import app; print(app.title)"
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Write-Host '== Backend pytest =='
& $backendPython -m pytest
$testExitCode = $LASTEXITCODE
Pop-Location
exit $testExitCode
