import asyncio
import sqlalchemy as sa
from sqlalchemy import text
from pcm.core.database import engine

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """))
        tables = [row[0] for row in result]
        print('Tables:', tables)
        print('\nroles exists:', 'roles' in tables)
        print('permissions exists:', 'permissions' in tables)
        print('role_permissions exists:', 'role_permissions' in tables)

asyncio.run(check())
