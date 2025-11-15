# Run the Event Intelligence Platform API
# This script activates the virtual environment and runs the app

Write-Host "🚀 Starting Event Intelligence Platform..." -ForegroundColor Green
Write-Host ""

# Navigate to Backend directory
Set-Location -Path "Backend"

# Run the app using the virtual environment's Python
& "..\venv\Scripts\python.exe" app.py

