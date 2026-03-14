import asyncio
import asyncpg

async def fix_users_table():
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        user='pcm_user',
        password='pcm123',
        database='pcmdata_db'
    )
    
    try:
        print("Adding missing columns to users table...")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE NOT NULL")
        print("✓ Added is_locked")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP")
        print("✓ Added locked_until")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0 NOT NULL")
        print("✓ Added failed_login_attempts")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP")
        print("✓ Added password_changed_at")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_expires_at TIMESTAMP")
        print("✓ Added password_expires_at")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS ldap_dn VARCHAR(500)")
        print("✓ Added ldap_dn")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS ldap_groups JSON")
        print("✓ Added ldap_groups")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_ldap_user BOOLEAN DEFAULT FALSE NOT NULL")
        print("✓ Added is_ldap_user")
        
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_ldap_sync TIMESTAMP")
        print("✓ Added last_ldap_sync")
        
        await conn.execute("CREATE INDEX IF NOT EXISTS ix_users_ldap_dn ON users(ldap_dn)")
        print("✓ Created index on ldap_dn")
        
        print("\n✅ Users table fixed successfully!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_users_table())
