from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from .config import settings as config
from urllib.parse import quote
from typing import AsyncGenerator


encoded_password = quote(config.DB_PASSWORD, safe="") # encodes all special characters, like @, :, /, and more in case your password contains them
DATABASE_URL = f"mysql+aiomysql://{config.DB_USERNAME}:{encoded_password}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_DATABASE}"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def reset_database():
    from app import models  # Ensure all models are imported
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        print("Database reset complete.")
