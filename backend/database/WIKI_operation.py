import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select, func

from .database import Wiki, WikiImage, async_session

logger = logging.getLogger(__name__)

# Конфигурация для загрузки файлов
UPLOAD_FOLDER = "uploads/wiki_images"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Дополнительные настройки безопасности
SECURE_UPLOAD = True  # Включить дополнительные проверки безопасности
BLOCK_EXECUTABLE_EXTENSIONS = True  # Блокировать исполняемые файлы

# Создаем папку для загрузок если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def is_allowed_file(filename: str) -> bool:
    """Проверяет, является ли файл разрешенным типом"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def is_valid_image_file(file) -> bool:
    """Проверяет, является ли файл действительно изображением"""
    import imghdr
    
    # Проверяем MIME-тип
    if not file.content_type or not file.content_type.startswith('image/'):
        return False
    
    # Проверяем содержимое файла
    try:
        # Читаем первые 32 байта для определения типа
        file.seek(0)
        header = file.read(32)
        file.seek(0)  # Возвращаемся в начало
        
        # Проверяем магические числа для изображений
        image_type = imghdr.what(None, h=header)
        if not image_type or image_type not in ['jpeg', 'jpg', 'png', 'gif', 'webp']:
            return False
            
        return True
    except Exception:
        return False

def check_file_security(file) -> bool:
    """Дополнительные проверки безопасности файла"""
    if not SECURE_UPLOAD:
        return True
    
    try:
        # Проверяем на наличие вредоносных паттернов
        file.seek(0)
        content = file.read(1024)  # Читаем первые 1KB
        file.seek(0)
        
        # Блокируем PHP код
        if b'<?php' in content or b'<?=' in content:
            return False
        
        # Блокируем JavaScript код
        if b'<script' in content or b'javascript:' in content:
            return False
        
        # Блокируем HTML теги
        if b'<html' in content or b'<!DOCTYPE' in content:
            return False
        
        # Блокируем исполняемые файлы
        if BLOCK_EXECUTABLE_EXTENSIONS:
            dangerous_patterns = [
                b'MZ',  # Windows PE
                b'\x7fELF',  # Linux ELF
                b'#!/',  # Shebang
            ]
            for pattern in dangerous_patterns:
                if content.startswith(pattern):
                    return False
        
        return True
    except Exception:
        return False

def get_safe_filename(filename: str) -> str:
    """Генерирует безопасное имя файла"""
    import uuid
    ext = Path(filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return safe_name

async def create_wiki(description: str, person_id: int, created_by: Optional[str] = None):
    # Обрезаем лишние пробелы, но сохраняем переносы строк
    if description:
        # Обрабатываем каждую строку отдельно, чтобы сохранить переносы
        lines = description.strip().split('\n')
        # Убираем лишние пробелы в каждой строке, но сохраняем пустые строки для переносов
        processed_lines = []
        for line in lines:
            processed_lines.append(' '.join(line.split()) if line.strip() else '')
        description = '\n'.join(processed_lines)
    
    async with async_session() as session:
        wiki = Wiki(
            description=description,
            person_id=person_id,
            created_by=created_by
        )
        session.add(wiki)
        try:
            await session.commit()
            await session.refresh(wiki)
            return wiki
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during wiki creation: {e}")
            raise

async def update_wiki(wiki_id: int, description: str, updated_by: Optional[str] = None):
    # Обрезаем лишние пробелы, но сохраняем переносы строк
    if description:
        # Обрабатываем каждую строку отдельно, чтобы сохранить переносы
        lines = description.strip().split('\n')
        # Убираем лишние пробелы в каждой строке, но сохраняем пустые строки для переносов
        processed_lines = []
        for line in lines:
            processed_lines.append(' '.join(line.split()) if line.strip() else '')
        description = '\n'.join(processed_lines)
    
    async with async_session() as session:
        query = select(Wiki).where(Wiki.id == wiki_id)
        result = await session.execute(query)
        wiki_entry = result.scalar_one_or_none()

        if wiki_entry is None:
            logger.error(f"Wiki entry with id {wiki_id} does not exist")
            raise ValueError(f"Wiki entry with id {wiki_id} does not exist")
        
        wiki_entry.description = description
        wiki_entry.updated_at = datetime.utcnow()
        if updated_by:
            wiki_entry.created_by = updated_by
            
        await session.commit()
        await session.refresh(wiki_entry)
        return wiki_entry

async def get_wiki_by_teacher_id(person_id: int):
    async with async_session() as session:
        query = select(Wiki).where(Wiki.person_id == person_id)
        result = await session.execute(query)
        wiki_entries = result.scalars().all()

        if not wiki_entries:
            logger.error(f"No wiki entries found for teacher id {person_id}")
            return []
        
        return wiki_entries

async def get_wiki_by_id(wiki_id: int):
    """Получить wiki по ID"""
    async with async_session() as session:
        query = select(Wiki).where(Wiki.id == wiki_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

async def upload_wiki_image(wiki_id: int, file, uploaded_by: Optional[str] = None) -> WikiImage:
    """Загрузить изображение для wiki"""
    if not file or not file.filename:
        raise ValueError("No file provided")
    
    if not is_allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Проверяем, что файл действительно является изображением
    if not is_valid_image_file(file):
        raise ValueError("File is not a valid image. Content validation failed.")
    
    # Дополнительные проверки безопасности
    if not check_file_security(file):
        raise ValueError("File contains potentially dangerous content. Security check failed.")
    
    # Проверяем размер файла
    file.seek(0, 2)  # Перемещаемся в конец файла
    file_size = file.tell()
    file.seek(0)  # Возвращаемся в начало
    
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Генерируем безопасное имя файла
    safe_filename = get_safe_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    
    # Сохраняем файл
    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file, f)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise ValueError("Error saving file")
    
    # Сохраняем информацию в базу данных
    async with async_session() as session:
        wiki_image = WikiImage(
            wiki_id=wiki_id,
            filename=safe_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type or 'application/octet-stream',
            uploaded_by=uploaded_by
        )
        
        session.add(wiki_image)
        try:
            await session.commit()
            await session.refresh(wiki_image)
            return wiki_image
        except Exception as e:
            await session.rollback()
            # Удаляем файл если не удалось сохранить в БД
            try:
                os.remove(file_path)
            except:
                pass
            logger.error(f"Error during image upload: {e}")
            raise

async def get_wiki_images(wiki_id: int) -> List[WikiImage]:
    """Получить все изображения для wiki"""
    async with async_session() as session:
        query = select(WikiImage).where(WikiImage.wiki_id == wiki_id)
        result = await session.execute(query)
        return result.scalars().all()

async def delete_wiki_image(image_id: int) -> bool:
    """Удалить изображение wiki"""
    async with async_session() as session:
        query = select(WikiImage).where(WikiImage.id == image_id)
        result = await session.execute(query)
        wiki_image = result.scalar_one_or_none()
        
        if not wiki_image:
            return False
        
        # Удаляем файл
        try:
            if os.path.exists(wiki_image.file_path):
                os.remove(wiki_image.file_path)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
        
        # Удаляем запись из БД
        await session.delete(wiki_image)
        await session.commit()
        return True

async def get_wiki_with_images(wiki_id: int):
    """Получить wiki с изображениями"""
    async with async_session() as session:
        query = select(Wiki).where(Wiki.id == wiki_id)
        result = await session.execute(query)
        wiki = result.scalar_one_or_none()
        
        if wiki:
            # Загружаем изображения отдельным запросом
            images_query = select(WikiImage).where(WikiImage.wiki_id == wiki_id)
            images_result = await session.execute(images_query)
            images = images_result.scalars().all()
            
            # Создаем словарь с данными wiki и изображениями
            wiki_data = {
                'id': wiki.id,
                'person_id': wiki.person_id,
                'description': wiki.description,
                'created_at': wiki.created_at,
                'updated_at': wiki.updated_at,
                'created_by': wiki.created_by,
                'images': images
            }
            return wiki_data
        
        return None

