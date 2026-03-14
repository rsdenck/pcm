import asyncio
import asyncpg

async def add_permissions_column():
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        user='pcm_user',
        password='pcm123',
        database='pcmdata_db'
    )
    
    try:
        print("Adding permissions column to users table...")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS permissions JSON")
        print("✅ Permissions column added successfully!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(add_permissions_column())
