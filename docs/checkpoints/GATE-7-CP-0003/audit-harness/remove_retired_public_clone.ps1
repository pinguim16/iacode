$ErrorActionPreference = 'Stop'
$retiredCloneTarget = 'E:\iacode\var\gate7-sealed-public-20261019-181247'
$retiredCloneParent = 'E:\iacode\var'
$retiredCloneResolved = (Resolve-Path -LiteralPath $retiredCloneTarget).Path
if ($retiredCloneResolved -cne $retiredCloneTarget -or
    -not $retiredCloneResolved.StartsWith($retiredCloneParent + '\', [StringComparison]::OrdinalIgnoreCase) -or
    ((Get-Item -LiteralPath $retiredCloneResolved).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    throw 'Exact retired runtime clone containment not proved'
}
$retiredCloneReceipt = Get-Content -LiteralPath 'E:\iacode\docs\checkpoints\GATE-7-CP-0003\retired-clone-observations\run-0001.json' -Raw | ConvertFrom-Json
if (-not $retiredCloneReceipt.eligibleForExactOwnerCleanup -or $retiredCloneReceipt.target -cne $retiredCloneResolved) {
    throw 'No matching completed eligibility observation'
}
$retiredCloneHead = & git -C $retiredCloneResolved rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $retiredCloneHead -cne '823cf164c6931dab7f957c92721ded7a916655bd') {
    throw 'Retired public subject changed'
}
$retiredCloneChanges = & git -C $retiredCloneResolved status --porcelain
if ($LASTEXITCODE -ne 0 -or $retiredCloneChanges) { throw 'Unique work appeared in retired clone' }
$retiredCloneProcesses = @(Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and $_.CommandLine.IndexOf('gate7-sealed-public-20261019-181247', [StringComparison]::OrdinalIgnoreCase) -ge 0
})
if ($retiredCloneProcesses.Count -ne 0) { throw 'Retired clone now has a process reference' }
Remove-Item -LiteralPath $retiredCloneResolved -Recurse -Force -ErrorAction Stop
if (Test-Path -LiteralPath $retiredCloneResolved) { throw 'Exact retired clone still exists' }
Write-Output 'EXACT_RECONSTRUCTIBLE_RETIRED_CLONE_REMOVED'
