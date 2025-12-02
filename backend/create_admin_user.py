"""
Create admin user using backend's actual password hashing
Run this from the backend directory
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to load .env
parent_dir = Path(__file__).parent.parent
env_file = parent_dir / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

from db.session import get_session, create_db_and_tables
from models import User
from api.auth import get_password_hash
from sqlmodel import select

def main():
    """Create admin user"""
    print("🔧 Creating admin user...")
    
    # Ensure database exists
    create_db_and_tables()
    
    session = next(get_session())
    
    try:
        # Check if user exists
        existing = session.exec(select(User).where(User.username == "admin")).first()
        
        if existing:
            print(f"⚠️  User 'admin' already exists!")
            print(f"   Updating password...")
            
            # Update password
            existing.hashed_password = get_password_hash("Admin123!")
            session.add(existing)
            session.commit()
            session.refresh(existing)
            
            print("✅ Password updated!")
        else:
            # Create new user
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
            
            print("✅ Admin user created!")
        
        print("\n🎉 Login Credentials:")
        print("   Username: admin")
        print("   Password: Admin123!")
        print("\nYou can now login at http://localhost:3000")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()

