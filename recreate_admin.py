import asyncio
import asyncpg
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def recreate_admin():
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        user='pcm_user',
        password='pcm123',
        database='pcmdata_db'
    )
    
    try:
        # Hash the password
        password = "Admin@123456"
        hashed = pwd_context.hash(password)
        
        print(f"Password hash length: {len(hashed)}")
        print(f"Hashed password: {hashed[:50]}...")
        
        # Update admin user
        print("\nUpdating admin user...")
        result = await conn.execute(
            """
            UPDATE users 
            SET hashed_password = $1,
                role = 'PROVIDER_ADMIN',
                is_active = true
            WHERE email = 'admin@pcm.local'
            """,
            hashed
        )
        print(f"✅ Admin user updated: {result}")
        
        # Verify
        row = await conn.fetchrow(
            "SELECT email, role, is_active FROM users WHERE email = 'admin@pcm.local'"
        )
        if row:
            print(f"\n✓ Verified:")
            print(f"  Email: {row['email']}")
            print(f"  Role: {row['role']}")
            print(f"  Active: {row['is_active']}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(recreate_admin())
