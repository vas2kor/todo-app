<#
.SYNOPSIS
    Stops the backend (FastAPI) and frontend (Vite) dev servers.

.DESCRIPTION
    Finds and kills any processes listening on the backend and frontend ports.

.PARAMETER BackendPort
    Port the FastAPI backend is running on. Default: 8000.

.PARAMETER FrontendPort
    Port the Vite frontend is running on. Default: 5173.

.EXAMPLE
    .\stop-dev.ps1

.EXAMPLE
    .\stop-dev.ps1 -BackendPort 8080 -FrontendPort 3000
#>
[CmdletBinding()]
param(
    [int]$BackendPort  = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"

function Stop-Port {
    param([int]$Port, [string]$Label)

    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host ("  {0,-20} port {1}  - not running" -f $Label, $Port) -ForegroundColor DarkGray
        return
    }

    $procIds = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($procId in $procIds) {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
    Write-Host ("  {0,-20} port {1}  - stopped (PID {2})" -f $Label, $Port, ($procIds -join ', ')) -ForegroundColor Green
}

Write-Host "Stopping dev servers..." -ForegroundColor Cyan
Stop-Port -Port $BackendPort  -Label "Backend  (FastAPI)"
Stop-Port -Port $FrontendPort -Label "Frontend (Vite)"
Write-Host "Done." -ForegroundColor Green
