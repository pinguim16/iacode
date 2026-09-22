<#
.SYNOPSIS
    Verify the IACode Gate 0 Foundation.

.DESCRIPTION
    A convenience wrapper. The verification itself is `scripts/iacode/verify.py`, which is Python
    driving Docker and runs identically on Windows and on POSIX; this exists so a Windows developer
    can type `.\verify.ps1` instead of remembering the interpreter and the path.

    Every argument is forwarded unchanged, so `.\verify.ps1 --fast` and `.\verify.ps1 --list` work
    exactly as the documented commands do.

    There is deliberately no logic here beyond locating the repository and choosing an interpreter.
    A wrapper that did more would be a second implementation of the verification, and the two would
    disagree the first time one of them was updated.

.EXAMPLE
    .\verify.ps1
    .\verify.ps1 --fast
    .\verify.ps1 --list
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Arguments
)

$ErrorActionPreference = 'Stop'
$repository = Split-Path -Parent $MyInvocation.MyCommand.Path

$interpreter = $null
foreach ($candidate in @('python', 'python3', 'py')) {
    $command = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($command) { $interpreter = $command.Source; break }
}
if (-not $interpreter) {
    Write-Error 'Python 3.12 or newer is required and was not found on PATH.'
    exit 1
}

& $interpreter (Join-Path $repository 'scripts/iacode/verify.py') @Arguments
exit $LASTEXITCODE
