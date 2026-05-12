param(
    # Skip Kroki Docker startup + health verification.
    [switch]$SkipDocker,
    # Skip storage backend bootstrap (local dirs or blob container check).
    [switch]$SkipStorage,
    # Skip Azure Search index create-if-missing + schema validation.
    [switch]$SkipIndex,
    # Print compact executed/skipped/failed summary at the end.
    [switch]$VerboseSkip
)

$ErrorActionPreference = "Stop"
$stepSummary = [ordered]@{
    Docker  = if ($SkipDocker) { "Skipped" } else { "Pending" }
    Storage = if ($SkipStorage) { "Skipped" } else { "Pending" }
    Index   = if ($SkipIndex) { "Skipped" } else { "Pending" }
}

function Invoke-SetupStep {
    param(
        [string]$Name,
        [scriptblock]$Action
    )
    Write-Host ""
    Write-Host "=== $Name ==="
    # Any exception from the action bubbles up to the caller so step status
    # can be recorded as Failed and the script exits immediately.
    & $Action
}

if (-not $SkipDocker) {
    try {
        Invoke-SetupStep -Name "Kroki Docker start" -Action {
            powershell -ExecutionPolicy Bypass -File ".\scripts\start-kroki.ps1"
            powershell -ExecutionPolicy Bypass -File ".\scripts\status-kroki.ps1"
        }
        $stepSummary.Docker = "Executed"
    } catch {
        $stepSummary.Docker = "Failed"
        throw
    }
} else {
    Write-Host "Skipping Docker step."
}

if (-not $SkipStorage) {
    try {
        Invoke-SetupStep -Name "Storage setup" -Action {
            Push-Location ".\backend"
            try {
                python ".\scripts\storage_setup.py"
            } finally {
                Pop-Location
            }
        }
        $stepSummary.Storage = "Executed"
    } catch {
        $stepSummary.Storage = "Failed"
        throw
    }
} else {
    Write-Host "Skipping storage step."
}

if (-not $SkipIndex) {
    try {
        Invoke-SetupStep -Name "Azure Search index setup" -Action {
            Push-Location ".\backend"
            try {
                python ".\scripts\ai_search_index.py" create-if-missing
                python ".\scripts\validate_ai_search_index.py"
            } finally {
                Pop-Location
            }
        }
        $stepSummary.Index = "Executed"
    } catch {
        $stepSummary.Index = "Failed"
        throw
    }
} else {
    Write-Host "Skipping index step."
}

Write-Host ""
Write-Host "Initial setup workflow completed."
if ($VerboseSkip) {
    Write-Host "Setup summary:"
    Write-Host (" - Docker : {0}" -f $stepSummary.Docker)
    Write-Host (" - Storage: {0}" -f $stepSummary.Storage)
    Write-Host (" - Index  : {0}" -f $stepSummary.Index)
}
