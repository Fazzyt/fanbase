import logging

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from backend.config import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Async Database Engine configuration
DATABASE_URL = f"postgresql+asyncpg://{config.database_user}:{config.database_password}@{config.database_host}/{config.database_name}"
engine = create_async_engine(
    DATABASE_URL,
    echo=config.debug_mode,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    full_name = Column(Text, nullable=False, unique=True, index=True)

class Quotes(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    quote = Column(Text, nullable=False, index=True)
    person_id = Column(Integer, nullable=False, index=True )
    



async def init_db():
    """
    Initialize the database and create tables.
    """
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as error:
            logger.error(f"Error creating tables: {error}")
