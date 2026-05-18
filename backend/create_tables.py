import asyncio
from app.models.database import engine, Base
from app.models.models import User, Exam, Submission

async def create_tables():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables created!")
    print("  - users")
    print("  - exams")
    print("  - submissions")

asyncio.run(create_tables())