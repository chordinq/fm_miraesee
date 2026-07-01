# Build MiraeseeApp (onedir) + release zip
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

& (Join-Path $PSScriptRoot "build.ps1")

$version = (python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])").Trim()
$releaseDir = Join-Path $Root "release"
$stagingRoot = Join-Path $releaseDir "_staging"
$packageName = "Miraesee-$version-win64"
$stagingDir = Join-Path $stagingRoot $packageName
$zipPath = Join-Path $releaseDir "$packageName.zip"
$distDir = Join-Path $Root "dist\MiraeseeApp"

if (Test-Path $stagingRoot) {
	Remove-Item $stagingRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $stagingDir -Force | Out-Null

Copy-Item (Join-Path $distDir "MiraeseeApp.exe") $stagingDir
Copy-Item (Join-Path $distDir "_internal") (Join-Path $stagingDir "_internal") -Recurse
python -c "from pathlib import Path; from build.bundle_prune import copy_release_assets; copy_release_assets(Path('.').resolve(), Path(r'$stagingDir') / 'assets')"
Copy-Item (Join-Path $Root "utils\miraesee_data_exporter.lua") $stagingDir

$readme = @"
Miraesee Tools v$version (Windows x64)

포함 파일
  MiraeseeApp.exe              시뮬레이터 UI
  _internal/                   앱 런타임 (삭제·이동 금지)
  assets/                      게임 스프라이트·설정·로컬라이제이션
  miraesee_data_exporter.lua   GameGuardian dump 추출 스크립트

=== 1. 게임에서 dump 추출 (Android + GameGuardian) ===
  1) 게임과 GameGuardian을 실행합니다.
  2) miraesee_data_exporter.lua 를 GG에서 실행합니다.
  3) 완료되면 dump가 클립보드에 복사됩니다.
  4) PC 클립보드로 옮깁니다 (에뮬 클립보드 공유 등).

=== 2. PC에서 dump 불러오기 ===
  1) MiraeseeApp.exe 실행 (폴더 전체를 함께 유지)
  2) dump 전문을 PC 클립보드에 붙여넣기
  3) 왼쪽 하단 LoadDump(↑ 아이콘) 클릭

=== 3. 화면 ===
  왼쪽 탭: Forge / Skills / Pets / Mounts / Tech Tree
  가운데: 소환·업그레이드 시뮬
  오른쪽: 컬렉션
  설정(⚙): UI 언어

앱 내 변경은 로컬 시뮬이며 게임 계정에 반영되지 않습니다.
Python 설치 불필요.
"@
Set-Content -Path (Join-Path $stagingDir "README.txt") -Value $readme -Encoding UTF8

if (Test-Path $zipPath) {
	Remove-Item $zipPath -Force
}
Compress-Archive -Path (Join-Path $stagingDir "*") -DestinationPath $zipPath -CompressionLevel Optimal

Remove-Item $stagingRoot -Recurse -Force

$exeMb = [math]::Round((Get-Item (Join-Path $distDir "MiraeseeApp.exe")).Length / 1MB, 1)
$zipMb = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)
Write-Host ""
Write-Host "Release: $zipPath"
Write-Host "  MiraeseeApp.exe  ${exeMb} MB"
Write-Host "  zip              ${zipMb} MB"
