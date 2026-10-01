import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DB_URL = "postgresql+asyncpg://unifiedrx:changeme_dev_password@localhost:5432/unifiedrx_db"

async def check():
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT medicine_a, medicine_b, severity, evidence FROM drug_interaction_knowledge_base WHERE medicine_a ILIKE '%warfarin%' OR medicine_b ILIKE '%warfarin%'"))
        for row in res.fetchall():
            print(row)

asyncio.run(check())