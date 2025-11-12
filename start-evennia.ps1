# Start Evennia from the correct directory
# Usage: .\start-evennia.ps1

$ProjectRoot = "C:\Users\dasbl\PycharmProjects\TheBeckoningMU"
Set-Location $ProjectRoot

Write-Host "Starting Evennia from: $ProjectRoot" -ForegroundColor Green
& evennia start
