import logging

from sqlalchemy import select

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


async def get_all_quote_by_person(person_id: int):
    async with async_session() as session:
        query = select(Quotes).where(Quotes.person_id == person_id)
        try:
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting all person: {e}")
            return None