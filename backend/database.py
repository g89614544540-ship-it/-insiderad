"""База данных."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_async_engine("sqlite+aiosqlite:///./insiderad.db")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        from models import User, Campaign, AdView, Withdrawal, Feedback
        await conn.run_sync(Base.metadata.create_all)
    print("База данных создана!")