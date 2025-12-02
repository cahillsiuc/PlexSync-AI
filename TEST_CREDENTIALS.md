# Test User Credentials

## Default Test Account

You can use these credentials to login to the application:

**Email:** `admin@plexsync.ai`  
**Username:** `admin`  
**Password:** `Admin123!`  
**Full Name:** `Admin User`

## How to Use

1. Go to http://localhost:3000
2. Click "Sign up" or go to the Register page
3. Enter the credentials above
4. After registration, you'll be automatically logged in

## Alternative: Create via API

If the backend is running, you can also register via the API:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@plexsync.ai",
    "username": "admin",
    "password": "Admin123!",
    "full_name": "Admin User"
  }'
```

Or use the API documentation at http://localhost:8000/docs

