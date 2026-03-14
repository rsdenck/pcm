import asyncio
import asyncpg
import bcrypt

async def recreate_admin():
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        user='pcm_user',
        password='pcm123',
        database='pcmdata_db'
    )
    
    try:
        # Hash the password using bcrypt directly
        password = "Admin@123456"
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        hashed_str = hashed.decode('utf-8')
        
        print(f"Password hash length: {len(hashed_str)}")
        print(f"Hashed password: {hashed_str}")
        
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
            hashed_str
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
        
        # Test password verification
        print("\n✓ Testing password verification...")
        stored_hash = await conn.fetchval(
            "SELECT hashed_password FROM users WHERE email = 'admin@pcm.local'"
        )
        if bcrypt.checkpw(password_bytes, stored_hash.encode('utf-8')):
            print("✅ Password verification successful!")
        else:
            print("❌ Password verification failed!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(recreate_admin())
