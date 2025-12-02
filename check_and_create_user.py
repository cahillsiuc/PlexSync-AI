"""
Check if admin user exists, create if not
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.db.session import get_session
from backend.models import User
from backend.api.auth import get_password_hash
from sqlmodel import select

def main():
    session = next(get_session())
    
    # Check if admin user exists
    user = session.exec(select(User).where(User.username == 'admin')).first()
    
    if user:
        print("✅ User 'admin' already exists!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
    else:
        print("❌ User 'admin' does NOT exist. Creating...")
        
        # Create admin user
        admin_user = User(
            email="admin@plexsync.ai",
            username="admin",
            full_name="Admin User",
            hashed_password=get_password_hash("Admin123!"),
            is_active=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: Admin123!")

if __name__ == "__main__":
    main()

