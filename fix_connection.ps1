Write-Host "=== StartupSaarthi Connection Fixer ===" -ForegroundColor Cyan
Write-Host "1. stopping conflicting processes..." -ForegroundColor Yellow
try {
    taskkill /F /IM python.exe /T 2>$null
    taskkill /F /IM node.exe /T 2>$null
} catch {
    Write-Host "No processes to kill."
}

Write-Host "2. Waiting for ports to clear..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "3. Starting Backend (New Window)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd d:\A_VERSE\StartupSaarthi; if (Test-Path venv) { .\venv\Scripts\activate }; python -m backend.main"

Write-Host "4. Starting Frontend (New Window)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd d:\A_VERSE\StartupSaarthi\startupsaarthi-ui; npm run dev"

Write-Host "=== Done! ===" -ForegroundColor Cyan
Write-Host "Please wait ~15 seconds for the backend to start."
Write-Host "Then refresh http://localhost:5173"
