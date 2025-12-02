# Quick Fix Guide

## If Login/Registration Not Working

### Issue 1: No User Account Exists
**Solution:** You need to register first!

1. Go to: http://localhost:3000/register
2. Fill in the form:
   - Full Name: Admin User
   - Email: admin@plexsync.ai
   - Username: admin
   - Password: Admin123!
3. Click "Create account"
4. You'll be automatically logged in

### Issue 2: Blank Screen
**Solution:**
1. Open Browser DevTools (F12)
2. Check Console tab for errors
3. Hard refresh: Ctrl+Shift+R
4. Check frontend server window for compilation errors

### Issue 3: Login Fails
**Possible causes:**
- User doesn't exist (register first!)
- Wrong username/password
- Backend not running

**Test:**
- Username: `admin`
- Password: `Admin123!`

### Issue 4: Registration Fails
**Check:**
- All fields filled?
- Username is unique?
- Email is valid format?
- Password is at least 8 characters?

## Quick Test

Try registering a new user:
1. Go to http://localhost:3000/register
2. Use any email/username/password
3. After registration, you'll be logged in automatically

## Still Not Working?

Share:
1. Browser console errors (F12 → Console)
2. Frontend server errors (PowerShell window)
3. What you see on screen

