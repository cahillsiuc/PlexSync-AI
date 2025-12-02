"""
Directly create a user in the database (bypasses API)
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from root directory
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment from {env_path}")
else:
    print(f"⚠️  .env file not found at {env_path}")

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.db.session import get_session, create_db_and_tables
from backend.models import User
from backend.api.auth import get_password_hash
from sqlmodel import select

def create_admin_user():
    """Create admin user directly in database"""
    print("🔧 Creating admin user directly in database...")
    
    # Ensure database tables exist
    create_db_and_tables()
    print("✅ Database tables initialized")
    
    # Get database session
    session = next(get_session())
    
    try:
        # Check if user already exists
        existing_user = session.exec(
            select(User).where(User.username == "admin")
        ).first()
        
        if existing_user:
            print(f"✅ User 'admin' already exists!")
            print(f"   ID: {existing_user.id}")
            print(f"   Username: {existing_user.username}")
            print(f"   Email: {existing_user.email}")
            print(f"   Active: {existing_user.is_active}")
            return existing_user
        
        # Create new admin user
        print("Creating new admin user...")
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
        print(f"   ID: {admin_user.id}")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: Admin123!")
        print("\n🎉 You can now login with:")
        print("   Username: admin")
        print("   Password: Admin123!")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_admin_user()

