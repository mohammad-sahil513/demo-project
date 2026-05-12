param(
    # Host port exposed for Kroki (container always listens on 8000).
    [int]$HostPort = 8001
)

$ErrorActionPreference = "Stop"

$dockerDesktopExe = Join-Path $Env:ProgramFiles "Docker\Docker\Docker Desktop.exe"

function Test-DockerReady {
    try {
        docker info *> $null
        return $true
    } catch {
        return $false
    }
}

function Test-KrokiHealthy {
    param([int]$Port)
    # Kroki exposes a simple health endpoint for readiness checks.
    $healthUrl = "http://127.0.0.1:$Port/health"
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI is not installed or not on PATH."
}

if (-not (Test-DockerReady)) {
    if (-not (Test-Path $dockerDesktopExe)) {
        throw "Docker engine is not running and Docker Desktop was not found at '$dockerDesktopExe'."
    }

    Write-Host "Starting Docker Desktop..."
    Start-Process -FilePath $dockerDesktopExe | Out-Null

    $maxWaitSeconds = 90
    $start = Get-Date
    while (-not (Test-DockerReady)) {
        if (((Get-Date) - $start).TotalSeconds -ge $maxWaitSeconds) {
            throw "Docker engine did not become ready within $maxWaitSeconds seconds."
        }
        Start-Sleep -Seconds 2
    }
}

if ($HostPort -ne 8001) {
    Write-Host "Note: backend default KROKI_URL uses port 8001. Update backend/.env if you change the host port."
}

if (Test-KrokiHealthy -Port $HostPort) {
    # Idempotent startup: if Kroki is already healthy, do not restart it.
    Write-Host "Kroki is already healthy on localhost:$HostPort. Skipping start."
    exit 0
}

Write-Host "Starting Kroki on localhost:$HostPort ..."
# Compose file reads this value as KROKI_HOST_PORT for host mapping.
$Env:KROKI_HOST_PORT = "$HostPort"
docker compose -f "docker-compose.kroki.yml" up -d

Write-Host "Kroki status:"
docker compose -f "docker-compose.kroki.yml" ps
