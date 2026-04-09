[CmdletBinding()]
param(
    [Alias("h")]
    [switch]$Help,

    [Parameter(Position = 0)]
    [string]$Version,

    [Parameter(Position = 1)]
    [string]$SourceRef = "develop/main",

    [Parameter(Position = 2)]
    [string]$PublicBase = "public/main"
)

$ErrorActionPreference = "Stop"

function Show-Usage {
    @"
Usage:
  powershell -ExecutionPolicy Bypass -File scripts/export_public_snapshot.ps1 <version> [source_ref] [public_base]

Examples:
  powershell -ExecutionPolicy Bypass -File scripts/export_public_snapshot.ps1 v0.8.2
  powershell -ExecutionPolicy Bypass -File scripts/export_public_snapshot.ps1 v0.8.2 develop/main public/main
  # works even if public/main does not exist yet

Defaults:
  source_ref  = develop/main
  public_base = public/main

This script:
  1) checks out export branch from public/main (or creates orphan if missing)
  2) overlays develop/main while excluding internal files
  3) removes excluded paths from snapshot
  4) creates a release snapshot commit
"@
}

if ($Help -or -not $Version -or $Version -in @("-h", "--help")) {
    Show-Usage
    exit 0
}

$exportBranch = "export-public"
$publicGitAuthorName = if ($env:PUBLIC_GIT_AUTHOR_NAME) { $env:PUBLIC_GIT_AUTHOR_NAME } else { "nyoki-mtl" }
$publicGitAuthorEmail = if ($env:PUBLIC_GIT_AUTHOR_EMAIL) { $env:PUBLIC_GIT_AUTHOR_EMAIL } else { "charmer.popopo@gmail.com" }

$excludePaths = @(
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursor/**",
    ".claude/**",
    "agent-docs/**",
    "_refs/**",
    ".sandbox/**",
    ".serena/**"
)

$removePaths = @(
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursor",
    ".claude",
    "agent-docs",
    "_refs",
    ".sandbox",
    ".serena"
)

$repoRoot = (& git rev-parse --show-toplevel).Trim()
if (-not $repoRoot) {
    throw "Failed to resolve repository root."
}

Push-Location $repoRoot
try {
    Write-Host "[1/5] Fetch remotes"
    & git fetch develop
    & git fetch public

    $null = & git rev-parse --verify --quiet $PublicBase 2>$null
    $hasPublicBase = ($LASTEXITCODE -eq 0)

    Write-Host "[2/5] Prepare export branch"
    if ($hasPublicBase) {
        Write-Host "  base: $PublicBase"
        & git switch -C $exportBranch $PublicBase
    }
    else {
        Write-Host "  base: (none, creating orphan branch)"
        & git switch --orphan $exportBranch
        & git rm -r --ignore-unmatch . *> $null
        & git clean -fd *> $null
    }

    Write-Host "[3/5] Overlay $SourceRef with excluded dev-only paths"
    $checkoutArgs = @($SourceRef, "--", ".")
    foreach ($path in $excludePaths) {
        $checkoutArgs += ":(exclude)$path"
    }
    & git checkout @checkoutArgs

    Write-Host "[4/5] Remove excluded paths from public snapshot"
    & git rm -r --ignore-unmatch @removePaths *> $null
    foreach ($path in $removePaths) {
        $absolutePath = Join-Path $repoRoot $path
        if (Test-Path -LiteralPath $absolutePath) {
            Remove-Item -LiteralPath $absolutePath -Recurse -Force
        }
    }

    Write-Host "[5/5] Reflect deletions from $SourceRef"
    if ($hasPublicBase) {
        $deletedPaths = & git diff --name-only --diff-filter=D "$PublicBase..$SourceRef"
        foreach ($path in $deletedPaths) {
            if (-not [string]::IsNullOrWhiteSpace($path)) {
                & git rm --ignore-unmatch -- $path *> $null
            }
        }
    }

    & git add -A
    & git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "No changes to export."
        exit 0
    }

    $env:GIT_AUTHOR_NAME = $publicGitAuthorName
    $env:GIT_AUTHOR_EMAIL = $publicGitAuthorEmail
    $env:GIT_COMMITTER_NAME = $publicGitAuthorName
    $env:GIT_COMMITTER_EMAIL = $publicGitAuthorEmail
    & git commit -m "Release $Version"

    @"
Snapshot commit created on branch '$exportBranch'.
Next:
  git push public HEAD:main
"@
}
finally {
    Pop-Location
}
