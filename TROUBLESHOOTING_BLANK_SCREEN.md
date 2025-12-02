# Troubleshooting Blank Screen

If you're seeing a blank screen, follow these steps:

## Step 1: Check Browser Console

1. Open your browser (Chrome/Edge/Firefox)
2. Press **F12** to open Developer Tools
3. Click on the **Console** tab
4. Look for any **red error messages**

Common errors you might see:
- `Cannot find module '@/...'` - Path alias issue
- `Failed to resolve import` - Missing dependency
- `Uncaught TypeError` - JavaScript error
- `ReferenceError` - Undefined variable

## Step 2: Check Frontend Server Window

Look at the PowerShell window running `npm run dev`. You should see:
- ✅ `VITE v5.x.x ready in xxx ms`
- ✅ `➜  Local:   http://localhost:3000/`

If you see **red error messages**, note them down.

## Step 3: Common Fixes

### Fix 1: Restart Frontend Server

1. In the frontend PowerShell window, press `Ctrl+C` to stop
2. Run: `npm run dev` again
3. Wait 10-15 seconds
4. Refresh browser (F5)

### Fix 2: Clear Browser Cache

1. Press `Ctrl+Shift+Delete`
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh the page (F5)

### Fix 3: Check for Missing Dependencies

In the frontend directory:
```powershell
cd frontend
npm install
npm run dev
```

### Fix 4: Hard Refresh

- **Windows/Linux:** `Ctrl+Shift+R` or `Ctrl+F5`
- **Mac:** `Cmd+Shift+R`

## Step 4: Verify Files Exist

Make sure these files exist:
- ✅ `frontend/src/main.tsx`
- ✅ `frontend/src/App.tsx`
- ✅ `frontend/src/index.css`
- ✅ `frontend/index.html`

## Step 5: Check Network Tab

1. Open DevTools (F12)
2. Go to **Network** tab
3. Refresh the page
4. Look for any files with **red status codes** (404, 500, etc.)

## Quick Test

Try accessing the raw HTML:
- Open: http://localhost:3000
- Right-click → "View Page Source"
- You should see the HTML with `<div id="root"></div>`

If you see the HTML but blank screen, it's a JavaScript error.

## Still Not Working?

Share the error messages from:
1. Browser Console (F12 → Console tab)
2. Frontend server window (PowerShell running npm run dev)

