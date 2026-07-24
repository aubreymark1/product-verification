$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot 'frontend'

Start-Process powershell -ArgumentList @(
  '-NoExit',
  '-ExecutionPolicy', 'Bypass',
  '-Command', "Set-Location -LiteralPath '$frontendRoot'; npm run dev"
)

