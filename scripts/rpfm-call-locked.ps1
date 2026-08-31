param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ToolName,

    [Parameter(Position = 1)]
    [string]$ArgumentsJson = "{}"
)

$mutexName = "Local\ComputationalTotalWarRpfmResearch"
$createdNew = $false
$mutex = [System.Threading.Mutex]::new($false, $mutexName, [ref]$createdNew)
$acquired = $false

try {
    try {
        $acquired = $mutex.WaitOne([TimeSpan]::FromMinutes(15))
    }
    catch [System.Threading.AbandonedMutexException] {
        $acquired = $true
    }

    if (-not $acquired) {
        throw "Timed out waiting for the shared RPFM research lock."
    }

    & node (Join-Path $PSScriptRoot "rpfm-call.mjs") $ToolName $ArgumentsJson
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    if ($acquired) {
        $mutex.ReleaseMutex()
    }
    $mutex.Dispose()
}
