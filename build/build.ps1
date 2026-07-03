# Build MiraeseeApp (onedir)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
python scripts/verify_app_imports.py
pyinstaller build/MiraeseeApp.spec --noconfirm
python -c "from pathlib import Path; from build.bundle_prune import copy_release_assets; copy_release_assets(Path('.').resolve(), Path('dist/MiraeseeApp/assets'))"
$distDir = Join-Path (Get-Location) "dist\MiraeseeApp"
$exe = Join-Path $distDir "MiraeseeApp.exe"
$sizeMb = [math]::Round((Get-Item $exe).Length / 1MB, 1)
Write-Host ""
Write-Host "Done: dist/MiraeseeApp/ ($sizeMb MB exe + _internal + assets)"
Write-Host "Run this exe (NOT build/MiraeseeApp/MiraeseeApp.exe):"
Write-Host "  $exe"
