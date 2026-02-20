# Build Lambda deployment package
# Run from the project root: powershell -File deploy/build_lambda.ps1
#
# WHY PLATFORM FLAGS?
# pip on Windows downloads Windows wheels. Lambda runs on Amazon Linux 2 (x86_64).
# pydantic-core (Rust), and any other C-extension packages would silently fail at
# runtime on Lambda if installed with Windows wheels.
# --platform manylinux2014_x86_64 forces pip to download the correct Linux wheels
# even when running on Windows.

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
$PKG  = "$ROOT\deploy\lambda_package"

Write-Host "Cleaning old package..." -ForegroundColor Cyan
if (Test-Path $PKG) { Remove-Item $PKG -Recurse -Force }
New-Item -ItemType Directory -Path $PKG | Out-Null

Write-Host "Installing Linux-compatible dependencies (manylinux2014_x86_64)..." -ForegroundColor Cyan
pip install `
    --platform manylinux2014_x86_64 `
    --implementation cp `
    --python-version 311 `
    --only-binary=:all: `
    -r "$ROOT\backend\requirements-lambda.txt" `
    -t $PKG `
    --quiet

Write-Host "Copying source files..." -ForegroundColor Cyan
Copy-Item "$ROOT\backend\main.py"  -Destination $PKG
Copy-Item "$ROOT\src"              -Destination "$PKG\src"       -Recurse
Copy-Item "$ROOT\templates"        -Destination "$PKG\templates"  -Recurse
Copy-Item "$ROOT\assets"           -Destination "$PKG\assets"     -Recurse -ErrorAction SilentlyContinue

Write-Host "Zipping..." -ForegroundColor Cyan
$ZIP = "$ROOT\deploy\lambda.zip"
if (Test-Path $ZIP) { Remove-Item $ZIP }
Compress-Archive -Path "$PKG\*" -DestinationPath $ZIP

$sizeMB = [math]::Round((Get-Item $ZIP).Length / 1MB, 1)
Write-Host "Done! lambda.zip is $sizeMB MB" -ForegroundColor Green
Write-Host "Upload deploy\lambda.zip to AWS Lambda. Handler: main.handler" -ForegroundColor Yellow
