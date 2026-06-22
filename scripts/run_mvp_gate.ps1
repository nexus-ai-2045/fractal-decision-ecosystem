param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$GateArgs
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $repoRoot

$candidates = @(
    @{ Label = "py -3"; Command = "py"; Args = @("-3") },
    @{ Label = "python"; Command = "python"; Args = @() }
)

$python = $null

foreach ($candidate in $candidates) {
    $command = $candidate.Command
    $baseArgs = $candidate.Args
    try {
        $probeOutput = & $command @baseArgs -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $python = $candidate
            break
        }
    }
    catch {
        continue
    }
}

if ($null -eq $python) {
    Write-Error "Python 3.11+ was not found. Install Python or make either 'py -3' or 'python' available on PATH, then rerun this script."
    exit 1
}

Write-Host "Using Python command: $($python.Label)"
& $python.Command @($python.Args) -m scripts.mvp_gate_check @GateArgs
exit $LASTEXITCODE
