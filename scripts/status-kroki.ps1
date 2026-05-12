param(
    [int]$HostPort = 8001
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI is not installed or not on PATH."
}

Write-Host "Kroki container status:"
docker compose -f "docker-compose.kroki.yml" ps

$healthUrl = "http://127.0.0.1:$HostPort/health"
Write-Host "Checking Kroki health at $healthUrl ..."
try {
    $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "Kroki is healthy."
    } else {
        Write-Host "Kroki health check returned status $($response.StatusCode)."
    }
} catch {
    Write-Host "Kroki health check failed: $($_.Exception.Message)"
}
