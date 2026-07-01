# Build MiraeseeApp (onedir)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
python scripts/verify_app_imports.py
pyinstaller build/MiraeseeApp.spec --noconfirm
$exe = Join-Path (Get-Location) "dist\MiraeseeApp\MiraeseeApp.exe"
$sizeMb = [math]::Round((Get-Item $exe).Length / 1MB, 1)
Write-Host "Done: dist/MiraeseeApp/ ($sizeMb MB exe + _internal)"
