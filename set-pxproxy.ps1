<#
.SYNOPSIS
    Ensures px-proxy is running and sets proxy environment variables.

.DESCRIPTION
    - Refreshes PATH from Machine/User environment.
    - Starts px-proxy on localhost if not already running.
    - Sets HTTP_PROXY/HTTPS_PROXY/NO_PROXY for the current shell session.

.PARAMETER NoProxy
    Clears proxy variables and skips px-proxy startup.

.PARAMETER UpstreamProxy
    Upstream corporate proxy address.
    Default: rb-proxy-in.bosch.com:8080

.PARAMETER PxPort
    Local px-proxy listen port. Default: 3128

.EXAMPLE
    .\set-pxproxy.ps1

.EXAMPLE
    .\set-pxproxy.ps1 -NoProxy
#>
[CmdletBinding()]
param(
    [switch]$NoProxy,
    [string]$UpstreamProxy = "rb-proxy-in.bosch.com:8080",
    [int]$PxPort = 3128
)

$ErrorActionPreference = "Stop"
$pyScripts = Join-Path $env:APPDATA "Python\Python313\Scripts"

# Refresh PATH so px is discoverable in fresh shells.
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")
if (Test-Path $pyScripts) { $env:Path += ";$pyScripts" }

function Test-Port([int]$Port) {
    try { return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop) }
    catch { return $false }
}

if ($NoProxy) {
    Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
    Remove-Item Env:HTTP_PROXY -ErrorAction SilentlyContinue
    Remove-Item Env:NO_PROXY -ErrorAction SilentlyContinue
    Write-Host "Proxy variables cleared for current session." -ForegroundColor Yellow
    return
}

if (-not (Get-Command px -ErrorAction SilentlyContinue)) {
    Write-Error "px not found on PATH. Install it with: py -m pip install --user px-proxy"
}

if (Test-Port $PxPort) {
    Write-Host "px-proxy already running on 127.0.0.1:$PxPort" -ForegroundColor DarkGray
} else {
    Write-Host "Starting px-proxy on 127.0.0.1:$PxPort -> $UpstreamProxy" -ForegroundColor Cyan
    Start-Process -FilePath "px" `
        -ArgumentList @("--proxy=$UpstreamProxy", "--listen=127.0.0.1", "--port=$PxPort", "--gateway") `
        -WindowStyle Minimized | Out-Null

    $maxWaitSeconds = 8
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    while (($stopwatch.Elapsed.TotalSeconds -lt $maxWaitSeconds) -and -not (Test-Port $PxPort)) {
        # Busy wait with a short command that yields execution.
        [void](Get-Date)
    }

    if (-not (Test-Port $PxPort)) {
        Write-Error "px-proxy failed to start on port $PxPort."
    }
}

$env:HTTPS_PROXY = "http://127.0.0.1:$PxPort"
$env:HTTP_PROXY = "http://127.0.0.1:$PxPort"
$env:NO_PROXY = "localhost,127.0.0.1"

Write-Host "Proxy configured for this session:" -ForegroundColor Green
Write-Host "HTTPS_PROXY=$($env:HTTPS_PROXY)"
Write-Host "HTTP_PROXY=$($env:HTTP_PROXY)"
Write-Host "NO_PROXY=$($env:NO_PROXY)"
