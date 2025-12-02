# How to Start the Application

## ⚠️ Important: Terminal Hanging Issue

When running servers in the background, they may appear to "hang" because they're long-running processes. This is normal! The servers need to keep running to serve requests.

## Recommended: Use Separate Terminal Windows

Instead of running commands in the background, open **two separate terminal windows**:

### Terminal 1: Backend Server
```powershell
cd C:\Users\cahil\PlexSync-AI\backend
python main.py
```

You should see output like:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this terminal open** - the server needs to keep running.

### Terminal 2: Frontend Server
```powershell
cd C:\Users\cahil\PlexSync-AI\frontend
npm run dev
```

You should see output like:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

**Leave this terminal open** - the dev server needs to keep running.

## Quick Start Commands

### Option 1: Manual (Recommended)
Open two PowerShell windows and run:

**Window 1:**
```powershell
cd C:\Users\cahil\PlexSync-AI\backend
python main.py
```

**Window 2:**
```powershell
cd C:\Users\cahil\PlexSync-AI\frontend
npm run dev
```

### Option 2: PowerShell Script
Create a file `start-servers.ps1`:

```powershell
# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\cahil\PlexSync-AI\backend; python main.py"

# Wait a moment
Start-Sleep -Seconds 2

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\cahil\PlexSync-AI\frontend; npm run dev"
```

Then run: `.\start-servers.ps1`

## Verify Servers Are Running

Once started, check:
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Stopping Servers

Press `Ctrl+C` in each terminal window to stop the servers.

