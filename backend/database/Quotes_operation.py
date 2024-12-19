import logging

from sqlalchemy import select, func

from .database import Quotes, async_session

logger = logging.getLogger(__name__)

async def create_quote(quote_text: str, person_id: int):
    async with async_session() as session:
        quote = Quotes(
            quote=quote_text,
            person_id=person_id
        )
        session.add(quote)
        try:
            await session.commit()
            await session.refresh(quote)
            return quote
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during quote creation: {e}")
            raise

async def delete_quote(quote_id: int):
    async with async_session() as session:
        query = select(Quotes).where(Quotes.id == quote_id)
        result = await session.execute(query)
        quote = result.scalar_one_or_none()
        
        if quote is None:
            logger.error(f"Quote with id {quote_id} does not exist")
            raise ValueError(f"Quote with id {quote_id} does not exist")
        
        try:
            await session.delete(quote)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during quote deletion: {e}")
            raise

async def get_quote_count_by_person(person_id: int):
    async with async_session() as session:
        query = select(func.count(Quotes.id)).where(Quotes.person_id == person_id)
        result = await session.execute(query)
        return result.scalar()

async def get_all_quote_by_person(person_id: int):
    async with async_session() as session:
        query = select(Quotes).where(Quotes.person_id == person_id)
        try:
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting all person: {e}")
            return None
        
async def get_all_quote():
    async with async_session() as session:
        query = select(Quotes)
        try:
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting all quotes: {e}")
            return None