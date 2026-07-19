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
$probeCode = @"
import json
import sys
print(json.dumps({
    "marker": "fde-mvp-gate-python-probe",
    "ok": sys.version_info >= (3, 11),
    "version": list(sys.version_info[:3]),
    "executable": sys.executable,
}))
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
"@

function Test-PyenvShimFailure {
    param([string]$Text)

    return $Text -match "(?i)\bpyenv\b" -and (
        $Text -match "(?i)not found" -or
        $Text -match "(?i)no such command" -or
        $Text -match "(?i)version .* is not installed" -or
        $Text -match "(?i)command .* was found but .* could not be loaded"
    )
}

function ConvertFrom-MvpGateOutputJson {
    param([object[]]$OutputLines)

    $text = (($OutputLines | ForEach-Object { [string]$_ }) -join "`n").Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }

    try {
        return $text | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        $start = $text.IndexOf("{")
        $end = $text.LastIndexOf("}")
        if ($start -lt 0 -or $end -le $start) {
            return $null
        }

        try {
            return $text.Substring($start, $end - $start + 1) | ConvertFrom-Json -ErrorAction Stop
        }
        catch {
            return $null
        }
    }
}

function Test-MvpGateReallyRan {
    param([object[]]$OutputLines)

    $text = (($OutputLines | ForEach-Object { [string]$_ }) -join "`n").Trim()
    if ($text -match "FDE MVP GATE CHECK\s+(OK|ERROR)") {
        return $true
    }

    $json = ConvertFrom-MvpGateOutputJson -OutputLines $OutputLines
    if ($null -ne $json -and $null -ne $json.overall -and $null -ne $json.checks) {
        return $true
    }

    return $text -match '"overall"\s*:\s*"(ok|error)"' -and $text -match '"checks"\s*:'
}

function Test-MvpGateSucceeded {
    param([object[]]$OutputLines)

    $text = (($OutputLines | ForEach-Object { [string]$_ }) -join "`n").Trim()
    if ($text -match "FDE MVP GATE CHECK\s+OK") {
        return $true
    }

    $json = ConvertFrom-MvpGateOutputJson -OutputLines $OutputLines
    if ($null -ne $json -and $json.overall -eq "ok" -and $null -ne $json.checks) {
        return $true
    }

    return $text -match '"overall"\s*:\s*"ok"' -and $text -match '"checks"\s*:'
}

foreach ($candidate in $candidates) {
    $command = $candidate.Command
    $baseArgs = $candidate.Args
    try {
        $probeOutput = & $command @baseArgs -c $probeCode 2>&1
        $probeText = ($probeOutput | Out-String)
        if (Test-PyenvShimFailure $probeText) {
            Write-Warning "Skipping $($candidate.Label): pyenv shim is not usable for the MVP gate."
            continue
        }
        if ($LASTEXITCODE -eq 0) {
            $probeJson = $probeText | ConvertFrom-Json -ErrorAction Stop
            if ($probeJson.marker -eq "fde-mvp-gate-python-probe" -and $probeJson.ok -eq $true) {
                $candidate.Executable = [string]$probeJson.executable
                $candidate.Version = ($probeJson.version -join ".")
                $python = $candidate
                break
            }
        }
        else {
            Write-Warning "Skipping $($candidate.Label): Python 3.11+ probe failed."
        }
    }
    catch {
        $message = $_.Exception.Message
        if (Test-PyenvShimFailure $message) {
            Write-Warning "Skipping $($candidate.Label): pyenv shim is not usable for the MVP gate."
        }
        else {
            Write-Warning "Skipping $($candidate.Label): Python probe could not run."
        }
        continue
    }
}

if ($null -eq $python) {
    Write-Error "Python 3.11+ was not found. Install Python or make either 'py -3' or 'python' available on PATH without a broken pyenv shim, then rerun this script."
    exit 1
}

Write-Host "Using Python command: $($python.Label) ($($python.Version))"
$gateOutput = & $python.Command @($python.Args) -m scripts.mvp_gate_check @GateArgs 2>&1
$gateExitCode = $LASTEXITCODE
$gateOutput | ForEach-Object { Write-Output $_ }

if (-not (Test-MvpGateReallyRan $gateOutput)) {
    Write-Error "MVP gate did not produce the expected gate output. Treating this as a failed gate run."
    exit 1
}

if ($gateExitCode -eq 0 -and -not (Test-MvpGateSucceeded $gateOutput)) {
    Write-Error "MVP gate did not report success. Treating this as a failed gate run."
    exit 1
}

exit $gateExitCode
