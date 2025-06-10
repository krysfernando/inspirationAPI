from sqlalchemy.ext.declarative import declarative_base
from .config import settings as config
from urllib.parse import quote
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

encoded_password = quote(config.DB_PASSWORD, safe="") # encodes all special characters, like @, :, /, and more in case your password contains them
DATABASE_URL = f"mysql+aiomysql://{config.DB_USERNAME}:{encoded_password}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_DATABASE}"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
