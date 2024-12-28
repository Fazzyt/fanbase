import logging

from sqlalchemy import select

from .database import Person, async_session

logger = logging.getLogger(__name__)

async def create_person(fullname: str):
    async with async_session() as session:
        person = Person(
            full_name= fullname
        )
        session.add(person)
        try:
            await session.commit()
            await session.refresh(person)
            return person
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during person creation: {e}")
            raise

async def update_person(person_id: int, fullname: str):
    async with async_session() as session:
        query = select(Person).where(Person.id == person_id)
        result = await session.execute(query)
        person = result.scalar_one_or_none()  
        
        if person is None:
            logger.error(f"Person with id {person_id} does not exist")
            raise ValueError(f"Person with id {person_id} does not exist")
        
        person.full_name = fullname
        
        try:
            await session.commit()
            await session.refresh(person)
            return person
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during person update: {e}")
            raise

async def delete_person(person_id: int):
    async with async_session() as session:
        query = select(Person).where(Person.id == person_id)
        result = await session.execute(query)
        person = result.scalar_one_or_none()
        
        if person is None:
            logger.error(f"Person with id {person_id} does not exist")
            raise ValueError(f"Person with id {person_id} does not exist")
        
        try:
            await session.delete(person)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during person deletion: {e}")
            raise

async def get_person_by_name(full_name: str):
    async with async_session() as session:
        query = select(Person).where(Person.full_name == full_name)
        try:
            result = await session.execute(query)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting person by name={full_name}: {e}")
            return None

async def get_person_by_id(user_id: int):
    async with async_session() as session:
        query = select(Person).where(Person.id == user_id)
        try:
            result = await session.execute(query)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting person by name={user_id}: {e}")
            return None

async def get_all_person():
    async with async_session() as session:
        query = select(Person)
        try:
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting all person: {e}")
            return None