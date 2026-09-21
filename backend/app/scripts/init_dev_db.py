"""
Dev utility: creates all 15 tables in the database specified by DATABASE_URL.
"""

import asyncio
from app.models import Base
from app.core.database import engine


async def main():
    print("[*] Creating all 15 tables in database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(main())
