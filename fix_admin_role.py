import asyncio
import asyncpg

async def fix_admin_role():
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        user='pcm_user',
        password='pcm123',
        database='pcmdata_db'
    )
    
    try:
        print("Fixing admin user role...")
        result = await conn.execute(
            "UPDATE users SET role = 'PROVIDER_ADMIN' WHERE email = 'admin@pcm.local'"
        )
        print(f"✅ Admin role updated: {result}")
        
        # Verify
        row = await conn.fetchrow("SELECT email, role FROM users WHERE email = 'admin@pcm.local'")
        if row:
            print(f"✓ Verified: {row['email']} has role {row['role']}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_admin_role())
