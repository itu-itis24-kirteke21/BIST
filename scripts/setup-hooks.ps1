# ==========================================================
# BIST 100 Analiz Sistemi - Git Hook Kurulum Scripti
# ==========================================================
# Bu script, hooks/ klasorunun icerigini .git/hooks/'a kopyalar.
#
# Kullanim:
#   powershell -ExecutionPolicy Bypass -File scripts/setup-hooks.ps1
# ==========================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$HooksSource = Join-Path $ProjectRoot "hooks"
$HooksTarget = Join-Path $ProjectRoot ".git" "hooks"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  BIST Git Hook Kurulumu" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $HooksSource)) {
    Write-Host "  HATA: hooks/ klasoru bulunamadi!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $HooksTarget)) {
    Write-Host "  HATA: .git/hooks/ klasoru bulunamadi!" -ForegroundColor Red
    Write-Host "  Bu bir git reposu degil mi?" -ForegroundColor Red
    exit 1
}

$hookFiles = Get-ChildItem -Path $HooksSource -File

foreach ($hook in $hookFiles) {
    $dest = Join-Path $HooksTarget $hook.Name
    Copy-Item -Path $hook.FullName -Destination $dest -Force
    Write-Host "  [OK] $($hook.Name) -> .git/hooks/$($hook.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "  Hook kurulumu tamamlandi!" -ForegroundColor Green
Write-Host "  Commit oncesi pytest otomatik calisacak." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
