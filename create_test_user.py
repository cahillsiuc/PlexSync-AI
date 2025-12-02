"""
Quick script to create a test user account
"""
import requests
import json

# Backend API URL
API_URL = "http://localhost:8000"

# Test user credentials
user_data = {
    "email": "admin@plexsync.ai",
    "username": "admin",
    "password": "Admin123!",
    "full_name": "Admin User"
}

print("Creating test user account...")
print(f"Email: {user_data['email']}")
print(f"Username: {user_data['username']}")
print(f"Password: {user_data['password']}")
print()

try:
    response = requests.post(
        f"{API_URL}/api/auth/register",
        json=user_data,
        timeout=5
    )
    
    if response.status_code == 200:
        print("✅ User created successfully!")
        print("\nYou can now login with:")
        print(f"  Email: {user_data['email']}")
        print(f"  Username: {user_data['username']}")
        print(f"  Password: {user_data['password']}")
    elif response.status_code == 400:
        error = response.json().get("detail", "Unknown error")
        if "already registered" in str(error).lower():
            print("ℹ️  User already exists. You can use these credentials:")
            print(f"  Email: {user_data['email']}")
            print(f"  Username: {user_data['username']}")
            print(f"  Password: {user_data['password']}")
        else:
            print(f"❌ Error: {error}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend server.")
    print("   Make sure the backend is running on http://localhost:8000")
except Exception as e:
    print(f"❌ Error: {e}")

