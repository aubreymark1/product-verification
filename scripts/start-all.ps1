$repoRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot 'start-backend.ps1')
& (Join-Path $PSScriptRoot 'start-frontend.ps1')
Write-Host "Frontend: http://127.0.0.1:5173/video"
Write-Host "Backend:  http://127.0.0.1:8000/api/health"

