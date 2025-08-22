import logging
import os
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from backend.config import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Async Database Engine configuration
#DATABASE_URL = f"postgresql+asyncpg://{config.database_user}:{config.database_password}@{config.database_host}/{config.database_name}"
DATABASE_URL = f"sqlite+aiosqlite:///fanbase.db"
engine = create_async_engine(
    DATABASE_URL,
    echo=config.debug_mode,
    #future=True,
    #pool_pre_ping=True,
    #pool_size=10,
    #max_overflow=20,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    full_name = Column(Text, nullable=False, unique=True, index=True)

    wiki = relationship("Wiki", back_populates="person", uselist=False)

class Quotes(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    quote = Column(Text, nullable=False, index=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False, index=True)

    person = relationship("Person", backref="quotes")

class Wiki(Base):
    __tablename__ = "wiki"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False, index=True)
    description = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=True)  # Для отслеживания кто создал/редактировал

    person = relationship("Person", back_populates="wiki")
    images = relationship("WikiImage", back_populates="wiki", cascade="all, delete-orphan")

class WikiImage(Base):
    __tablename__ = "wiki_images"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    wiki_id = Column(Integer, ForeignKey('wiki.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = Column(String(100), nullable=True)

    wiki = relationship("Wiki", back_populates="images")



async def init_db():
    """
    Initialize the database and create tables.
    """
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as error:
            logger.error(f"Error creating tables: {error}")
