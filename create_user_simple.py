"""
Simple script to create admin user directly in SQLite database
Bypasses all FastAPI/Pydantic config requirements
"""
import sqlite3
from datetime import datetime, timezone
from passlib.context import CryptContext

# Use same password hashing as backend
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database path (same as backend uses)
DB_PATH = "./plexsync.db"

def create_admin_user():
    """Create admin user directly in SQLite database"""
    print("🔧 Creating admin user directly in database...")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists, create if not
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                full_name TEXT,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Check if user already exists
        cursor.execute("SELECT id, username, email FROM user WHERE username = ?", ("admin",))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  User 'admin' already exists!")
            print(f"   ID: {existing[0]}")
            print(f"   Username: {existing[1]}")
            print(f"   Email: {existing[2]}")
            print("   Updating password hash to match backend format...")
            
            # Update password hash
            password = "Admin123!"
            hashed = pwd_context.hash(password)
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                UPDATE user 
                SET hashed_password = ?, updated_at = ?
                WHERE username = ?
            """, (hashed, now, "admin"))
            
            conn.commit()
            print("✅ Password hash updated!")
            print("\n🎉 You can now login with:")
            print("   Username: admin")
            print("   Password: Admin123!")
            return
        
        # Hash password using same method as backend
        password = "Admin123!"
        hashed = pwd_context.hash(password)
        
        # Create user
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO user (email, username, full_name, hashed_password, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin@plexsync.ai",
            "admin",
            "Admin User",
            hashed,
            True,
            now,
            now
        ))
        
        conn.commit()
        
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Email: admin@plexsync.ai")
        print(f"   Password: Admin123!")
        print("\n🎉 You can now login with:")
        print("   Username: admin")
        print("   Password: Admin123!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()

