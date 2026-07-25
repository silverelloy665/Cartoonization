param(
    [switch] $AddToPath
)

# Downloads a static ffmpeg build and places it under ./tools/ffmpeg
set-StrictMode -Version Latest

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
# Build the tools directory path (don't Resolve-Path here to avoid the Resolve-Path error)
$toolsRoot = Join-Path $scriptRoot "..\tools"
$toolsRoot = [IO.Path]::GetFullPath($toolsRoot)
$toolsDir = Join-Path $toolsRoot "ffmpeg"
if (-not (Test-Path $toolsRoot)) {
    New-Item -ItemType Directory -Path $toolsRoot | Out-Null
}

$zipPath = Join-Path $toolsRoot "ffmpeg.zip"

$url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
Write-Host "Downloading ffmpeg from: $url"
try {
    Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Error "Download failed: $_"
    exit 1
}

Write-Host "Extracting ffmpeg..."
$tempExtract = Join-Path $toolsRoot "_ffmpeg_extract"
if (Test-Path $tempExtract) { Remove-Item -Recurse -Force $tempExtract }
New-Item -ItemType Directory -Path $tempExtract | Out-Null

try {
    Expand-Archive -LiteralPath $zipPath -DestinationPath $tempExtract -Force
} catch {
    Write-Error "Extraction failed: $_"
    exit 1
}

# Find the folder that contains ffmpeg.exe
$ffmpegFolder = Get-ChildItem -Path $tempExtract -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'bin\ffmpeg.exe') } | Select-Object -First 1
if (-not $ffmpegFolder) {
    Write-Error "Could not find ffmpeg.exe in the extracted archive."
    Remove-Item -Recurse -Force $tempExtract, $zipPath
    exit 1
}

if (Test-Path $toolsDir) { Remove-Item -Recurse -Force $toolsDir }
Move-Item -Path $ffmpegFolder.FullName -Destination $toolsDir

Remove-Item -Recurse -Force $tempExtract, $zipPath

Write-Host "ffmpeg installed to: $toolsDir"

if ($AddToPath) {
    $binPath = Join-Path $toolsDir 'bin'
    $current = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($current -notlike "*$binPath*") {
        $new = "$current;$binPath"
        [Environment]::SetEnvironmentVariable('Path', $new, 'User')
        Write-Host "Added $binPath to user PATH. You may need to restart your shell."
    } else {
        Write-Host "$binPath already on PATH."
    }
}

Write-Host "Done. Verify with: ffmpeg -version"
