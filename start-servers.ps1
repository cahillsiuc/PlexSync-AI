# Start Backend Server
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\cahil\PlexSync-AI\backend; python main.py"

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start Frontend Server
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\cahil\PlexSync-AI\frontend; npm run dev"

Write-Host "`nServers are starting in separate windows..." -ForegroundColor Green
Write-Host "`nServer URLs:" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`nPlease wait 10-15 seconds for servers to fully start..." -ForegroundColor Yellow
Write-Host "`nTo stop servers, press Ctrl+C in each window.`n" -ForegroundColor Yellow

