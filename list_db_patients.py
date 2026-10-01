import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DB_URL = "postgresql+asyncpg://unifiedrx:changeme_dev_password@localhost:5432/unifiedrx_db"

async def list_patients():
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT patient_id, name, health_code FROM patients"))
        for row in res.fetchall():
            print(row)

asyncio.run(list_patients())