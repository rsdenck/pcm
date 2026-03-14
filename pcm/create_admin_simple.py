"""
Simple script to create admin user directly in database
"""

import asyncio
import asyncpg
import bcrypt
from datetime import datetime
import uuid

async def create_admin():
    # Database connection
    conn = await asyncpg.connect(
        host="localhost",
        port=5433,
        user="pcm_user",
        password="pcm123",
        database="pcmdata_db"
    )
    
    try:
        # Check if admin exists
        existing = await conn.fetchrow(
            "SELECT id, email FROM users WHERE email = $1",
            "admin@pcm.local"
        )
        
        if existing:
            print("\n✅ Admin user already exists!")
            print(f"   Email: {existing['email']}")
            print(f"   ID: {existing['id']}")
            return
        
        # Create System tenant if not exists
        tenant_id = str(uuid.uuid4())
        existing_tenant = await conn.fetchrow(
            "SELECT id FROM tenants WHERE name = $1",
            "System"
        )
        
        if existing_tenant:
            tenant_id = existing_tenant['id']
            print(f"✅ Using existing System tenant: {tenant_id}")
        else:
            await conn.execute(
                """
                INSERT INTO tenants (id, name, slug, tenant_id, organization, owner, status, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                tenant_id,
                "System",
                "system",
                "SYSTEM-001",
                "PCM System",
                "System Administrator",
                "active",
                datetime.utcnow(),
                datetime.utcnow()
            )
            print(f"✅ Created System tenant: {tenant_id}")
        
        # Create admin user
        user_id = str(uuid.uuid4())
        password = "Admin@123456"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        await conn.execute(
            """
            INSERT INTO users (
                id, email, username, hashed_password, full_name,
                role, is_active, is_superuser, tenant_id,
                created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            user_id,
            "admin@pcm.local",
            "admin",
            hashed_password,
            "System Administrator",
            "provider_admin",
            True,
            True,
            tenant_id,
            datetime.utcnow(),
            datetime.utcnow()
        )
        
        print("\n" + "="*70)
        print("✅ ADMIN USER CREATED SUCCESSFULLY!")
        print("="*70)
        print(f"   Email:     admin@pcm.local")
        print(f"   Username:  admin")
        print(f"   Password:  Admin@123456")
        print(f"   User ID:   {user_id}")
        print(f"   Role:      provider_admin (PROVIDER_ADMIN)")
        print(f"   Superuser: True")
        print(f"   Tenant:    System ({tenant_id})")
        print("="*70)
        print("\n🔐 You can now login at: http://192.168.130.10:9000/")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    print("\n🚀 Creating admin user...")
    print("-" * 70)
    asyncio.run(create_admin())
    print("\n✅ Done!")
