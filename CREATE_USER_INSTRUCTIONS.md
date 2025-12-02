# How to Create Your Admin User

## Option 1: Use API Documentation (Recommended - Bypasses CORS)

1. **Open the API docs in your browser:**
   - Go to: http://localhost:8000/docs

2. **Find the registration endpoint:**
   - Look for `POST /api/auth/register`
   - Click on it to expand

3. **Click "Try it out"**

4. **Enter the following JSON in the request body:**
```json
{
  "email": "admin@plexsync.ai",
  "username": "admin",
  "password": "Admin123!",
  "full_name": "Admin User"
}
```

5. **Click "Execute"**

6. **You should see a success response with user details**

7. **Now go to http://localhost:3000 and login with:**
   - Username: `admin`
   - Password: `Admin123!`

---

## Option 2: Fix CORS and Use Web Interface

If the CORS error persists, try:

1. **Hard refresh your browser:**
   - Press `Ctrl + Shift + R` (or `Ctrl + F5`)

2. **Clear browser cache:**
   - Open DevTools (F12)
   - Right-click the refresh button
   - Select "Empty Cache and Hard Reload"

3. **Try registering again at:**
   - http://localhost:3000/register

4. **Fill in the form:**
   - Full Name: `Admin User`
   - Email: `admin@plexsync.ai`
   - Username: `admin`
   - Password: `Admin123!`

---

## Option 3: Use PowerShell (If API Docs Don't Work)

Run this command in PowerShell:

```powershell
$body = '{"email":"admin@plexsync.ai","username":"admin","password":"Admin123!","full_name":"Admin User"}'
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" -Method Post -Body $body -ContentType "application/json"
```

Then login at http://localhost:3000 with:
- Username: `admin`
- Password: `Admin123!`

---

## Troubleshooting

If you still get errors:

1. **Check backend is running:**
   - Visit http://localhost:8000/health
   - Should return `{"status":"healthy"}`

2. **Check frontend is running:**
   - Visit http://localhost:3000
   - Should show the login page

3. **Restart both servers:**
   - Stop both backend and frontend
   - Start them again

