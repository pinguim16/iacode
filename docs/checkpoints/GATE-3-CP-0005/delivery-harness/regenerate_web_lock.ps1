param(
    [string]$RepositoryRoot = "E:\iacode"
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath($RepositoryRoot)
$web = Join-Path $root "apps\web"
$package = Join-Path $web "package.json"
$lock = Join-Path $web "package-lock.json"
if (-not (Test-Path -LiteralPath $package -PathType Leaf)) {
    throw "package.json not found at $package"
}

$tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$temp = Join-Path $tempRoot ("iacode-lock-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $temp | Out-Null

try {
    Copy-Item -LiteralPath $package -Destination (Join-Path $temp "package.json")
    & docker run --rm --volume "${temp}:/work" --workdir /work `
        iacode/web-toolchain:0.1.0 `
        npm install --package-lock-only --ignore-scripts --save-exact
    if ($LASTEXITCODE -ne 0) {
        throw "npm lockfile regeneration failed with exit code $LASTEXITCODE"
    }
    $generated = Join-Path $temp "package-lock.json"
    if (-not (Test-Path -LiteralPath $generated -PathType Leaf)) {
        throw "npm succeeded without producing package-lock.json"
    }
    Copy-Item -LiteralPath $generated -Destination $lock -Force
}
finally {
    $resolved = [System.IO.Path]::GetFullPath($temp)
    if ($resolved.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -and
        [System.IO.Path]::GetFileName($resolved).StartsWith("iacode-lock-")) {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
