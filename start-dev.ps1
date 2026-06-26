<#
.SYNOPSIS
    Starts the backend (FastAPI) and frontend (Vite) dev servers.

.DESCRIPTION
    - Optionally sets up px-proxy first (skipped with -NoProxy).
    - Starts the FastAPI backend on port 8000.
    - Starts the Vite frontend dev server on port 5500.
    - Both servers run in separate windows by default.
    - Use -Foreground to block in the current terminal (backend only; frontend still opens a window).

.PARAMETER NoProxy
    Skip px-proxy setup.

.PARAMETER Foreground
    Run the backend in the current terminal instead of a new window.
    Frontend always starts in a new window.

.PARAMETER BackendPort
    Port for the FastAPI backend. Default: 8000.

.PARAMETER FrontendPort
    Port for the Vite frontend. Default: 5500.

.EXAMPLE
    .\start-dev.ps1

.EXAMPLE
    .\start-dev.ps1 -NoProxy

.EXAMPLE
    .\start-dev.ps1 -Foreground
#>
[CmdletBinding()]
param(
    [switch]$NoProxy,
    [switch]$Foreground,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5500
)

$ErrorActionPreference = "Stop"
$repoRoot    = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir  = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$python      = Join-Path $repoRoot ".venv\Scripts\python.exe"

function Test-Port([int]$Port) {
    try { return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop) }
    catch { return $false }
}

# --- Proxy ---
if (-not $NoProxy) {
    $proxyScript = Join-Path $repoRoot "set-pxproxy.ps1"
    if (Test-Path $proxyScript) {
        Write-Host "Setting up px-proxy..." -ForegroundColor Cyan
        & $proxyScript
    }
}

# --- Guards ---
if (-not (Test-Path $python)) {
    Write-Error "Python venv not found at $python. Run: python -m venv .venv then pip install -r backend\requirements.txt"
}
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Push-Location $frontendDir
    try { npm install } finally { Pop-Location }
}

# --- Backend ---
if (Test-Port $BackendPort) {
    Write-Host "Backend already running on port $BackendPort" -ForegroundColor DarkGray
} else {
    $uvicornArgs = "-m uvicorn app.main:app --reload --host 0.0.0.0 --port $BackendPort --app-dir `"$backendDir`""
    if ($Foreground) {
        Write-Host "Starting backend on http://localhost:$BackendPort (foreground)..." -ForegroundColor Cyan
        Start-Process -FilePath $python `
            -ArgumentList $uvicornArgs.Split(" ") `
            -NoNewWindow -Wait
    } else {
        Write-Host "Starting backend on http://localhost:$BackendPort ..." -ForegroundColor Cyan
        Start-Process -FilePath "powershell" -ArgumentList @(
            "-NoExit", "-NoProfile",
            "-Command", "& '$python' $uvicornArgs"
        )
    }
}

# --- Frontend ---
if (Test-Port $FrontendPort) {
    Write-Host "Frontend already running on port $FrontendPort" -ForegroundColor DarkGray
} else {
    Write-Host "Starting frontend on http://localhost:$FrontendPort ..." -ForegroundColor Cyan
    Start-Process -FilePath "powershell" -ArgumentList @(
        "-NoExit", "-NoProfile",
        "-Command", "Set-Location '$frontendDir'; npm run dev -- --host 0.0.0.0 --port $FrontendPort"
    )
}

Write-Host ""
Write-Host "Dev servers launched:" -ForegroundColor Green
Write-Host "  Frontend : http://localhost:$FrontendPort"
Write-Host "  Backend  : http://localhost:$BackendPort"
Write-Host "  API docs : http://localhost:$BackendPort/docs"
