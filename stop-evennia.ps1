# Stop Evennia from the correct directory
# Usage: .\stop-evennia.ps1

$ProjectRoot = "C:\Users\dasbl\PycharmProjects\TheBeckoningMU"
Set-Location $ProjectRoot

Write-Host "Stopping Evennia from: $ProjectRoot" -ForegroundColor Yellow
& evennia stop
