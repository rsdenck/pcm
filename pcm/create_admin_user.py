"""
Script para criar usuário admin com permissões máximas
Email: admin@pcm.local
Password: Admin@123456
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime
import uuid

from core.models.user import User, UserRole
from core.models.tenant import Tenant
from core.database import Base
from core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    """Create admin user with maximum permissions"""
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=True,
        future=True
    )
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Check if admin user already exists
            result = await session.execute(
                select(User).where(User.email == "admin@pcm.local")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("\n✅ Admin user already exists!")
                print(f"   Email: {existing_user.email}")
                print(f"   Username: {existing_user.username}")
                print(f"   ID: {existing_user.id}")
                print(f"   Role: {existing_user.role}")
                return
            
            # Create default tenant for admin
            result = await session.execute(
                select(Tenant).where(Tenant.name == "System")
            )
            system_tenant = result.scalar_one_or_none()
            
            if not system_tenant:
                system_tenant = Tenant(
                    id=str(uuid.uuid4()),
                    name="System",
                    organization="PCM System",
                    owner="System Administrator",
                    status="ACTIVE",
                    created_at=datetime.utcnow()
                )
                session.add(system_tenant)
                await session.flush()
                print(f"✅ Created System tenant: {system_tenant.id}")
            
            # Create admin user
            hashed_password = pwd_context.hash("Admin@123456")
            
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@pcm.local",
                username="admin",
                hashed_password=hashed_password,
                full_name="System Administrator",
                role=UserRole.PROVIDER_ADMIN,
                is_active=True,
                is_superuser=True,
                tenant_id=system_tenant.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(admin_user)
            await session.flush()
            
            print("\n" + "="*70)
            print("✅ ADMIN USER CREATED SUCCESSFULLY!")
            print("="*70)
            print(f"   Email:     admin@pcm.local")
            print(f"   Username:  admin")
            print(f"   Password:  Admin@123456")
            print(f"   User ID:   {admin_user.id}")
            print(f"   Role:      {admin_user.role.value} (PROVIDER_ADMIN)")
            print(f"   Superuser: {admin_user.is_superuser}")
            print(f"   Tenant:    {system_tenant.name} ({system_tenant.id})")
            print("="*70)
            
            # Commit transaction
            await session.commit()
            
            print("\n✅ All changes committed to database!")
            print("\n🔐 You can now login with these credentials at:")
            print("   http://192.168.130.10:9000/")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error creating admin user: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("\n🚀 Creating admin user...")
    print("-" * 70)
    asyncio.run(create_admin_user())
    print("\n✅ Done!")

