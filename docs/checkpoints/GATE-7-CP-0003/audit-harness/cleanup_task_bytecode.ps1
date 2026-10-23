# Remove only bytecode belonging to explicitly declared new source files of this checkpoint.
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..'))
$taskCheckpoint = Join-Path $taskRoot 'docs\checkpoints\GATE-7-CP-0003'
$taskOutput = Join-Path $taskCheckpoint 'LOCAL-BYTECODE-CLEANUP.json'
if (Test-Path -LiteralPath $taskOutput) { throw 'Do not replay a completed cache disposal.' }
$taskState = Get-Content -LiteralPath (Join-Path $taskCheckpoint 'STATE.json') -Raw |
    ConvertFrom-Json
if ($taskState.baseCommit -notmatch '^[a-f0-9]{40}$') { throw 'Exact baseline required.' }
$taskInventory = Get-Content -LiteralPath (Join-Path $taskCheckpoint 'FILES.json') -Raw |
    ConvertFrom-Json
$taskBaseNames = @(& git -C $taskRoot ls-tree -r --name-only $taskState.baseCommit)
if ($LASTEXITCODE -ne 0) { throw 'Actual baseline enumeration failed.' }
$taskCandidates = @()
foreach ($taskEntry in $taskInventory.filesCreated) {
    $taskRelative = $taskEntry.path
    if (-not $taskRelative.EndsWith('.py')) { continue }
    if (-not ($taskRelative.StartsWith('scripts/') -or
              $taskRelative.StartsWith('tests/') -or
              $taskRelative.StartsWith('docs/checkpoints/GATE-7-CP-0003/audit-harness/'))) {
        continue
    }
    if ($taskRelative -cin $taskBaseNames) { throw 'A baseline source cannot claim a new cache.' }
    $taskSource = [IO.Path]::GetFullPath((Join-Path $taskRoot $taskRelative))
    if (-not $taskSource.StartsWith($taskRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Source escaped the workspace.'
    }
    $taskSourceItem = Get-Item -LiteralPath $taskSource -Force
    if ($taskSourceItem.PSIsContainer) { throw 'Regular source required.' }
    $taskCache = Join-Path $taskSourceItem.DirectoryName '__pycache__'
    if (-not (Test-Path -LiteralPath $taskCache)) { continue }
    $taskAncestor = Get-Item -LiteralPath $taskCache -Force
    while ($null -ne $taskAncestor -and $taskAncestor.FullName.Length -ge $taskRoot.Length) {
        if ($taskAncestor.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw 'Redirected cache ancestor refused.'
        }
        if ($taskAncestor.FullName -eq $taskRoot) { break }
        $taskAncestor = $taskAncestor.Parent
    }
    $taskPattern = '^' + [regex]::Escape($taskSourceItem.BaseName) +
        '\.cpython-313(?:\.opt-\d+)?\.pyc$'
    foreach ($taskFile in @(Get-ChildItem -LiteralPath $taskCache -File -Force)) {
        if ($taskFile.Name -notmatch $taskPattern) { continue }
        if ($taskFile.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw 'Redirected bytecode refused.'
        }
        $taskCandidates += [pscustomobject]@{
            source = $taskRelative
            path = $taskFile.FullName
            bytes = $taskFile.Length
            sha256 = (Get-FileHash -LiteralPath $taskFile.FullName -Algorithm SHA256).Hash.ToLower()
        }
    }
}
$taskCandidates = @($taskCandidates | Sort-Object path -Unique)
# All exact targets were validated before the first effect. No recursive deletion or broad clean.
foreach ($taskCandidate in $taskCandidates) {
    Remove-Item -LiteralPath $taskCandidate.path -Force
}
$taskRemaining = @($taskCandidates | Where-Object { Test-Path -LiteralPath $_.path })
$taskReport = [ordered]@{
    kind = 'DECLARED_NEW_TASK_SOURCE_BYTECODE_ONLY'
    observedAt = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    baseCommit = $taskState.baseCommit
    removed = $taskCandidates
    removedFiles = $taskCandidates.Count
    removedBytes = ($taskCandidates | Measure-Object bytes -Sum).Sum
    remainingCandidates = $taskRemaining.Count
    preexistingOrUnclaimedCachesPreserved = $true
    recursiveDeletionUsed = $false
    sourceOrEvidenceFilesDeleted = $false
    result = $(if ($taskRemaining.Count -eq 0) { 'PASS' } else { 'FAIL' })
}
[IO.File]::WriteAllText($taskOutput, ($taskReport | ConvertTo-Json -Depth 8) + "`n",
    [Text.UTF8Encoding]::new($false))
[pscustomobject]@{ result = $taskReport.result; removedFiles = $taskCandidates.Count;
    remainingCandidates = $taskRemaining.Count } | ConvertTo-Json
if ($taskRemaining.Count -ne 0) { exit 1 }
