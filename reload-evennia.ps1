# Reload Evennia from the correct directory
# Usage: .\reload-evennia.ps1

$ProjectRoot = "C:\Users\dasbl\PycharmProjects\TheBeckoningMU"
Set-Location $ProjectRoot

Write-Host "Reloading Evennia from: $ProjectRoot" -ForegroundColor Cyan
& evennia reload
