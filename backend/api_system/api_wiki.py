import logging
import os
from quart import Blueprint, jsonify, request, current_app, send_file
from werkzeug.utils import secure_filename

from backend.database import WIKI_operation

wiki_bp = Blueprint("wiki", __name__)
logger = logging.getLogger(__name__)

@wiki_bp.route("/api/v1/wiki/<int:wiki_id>", methods=["GET"])
async def get_wiki(wiki_id: int):
    """Получить wiki по ID с изображениями"""
    try:
        wiki_data = await WIKI_operation.get_wiki_with_images(wiki_id)
        if not wiki_data:
            return jsonify({
                "error": "Wiki not found",
                "status": 404
            }), 404
        
        return jsonify({
            "wiki": {
                "id": wiki_data['id'],
                "person_id": wiki_data['person_id'],
                "description": wiki_data['description'],
                "created_at": wiki_data['created_at'].isoformat() if wiki_data['created_at'] else None,
                "updated_at": wiki_data['updated_at'].isoformat() if wiki_data['updated_at'] else None,
                "created_by": wiki_data['created_by'],
                "images": [
                    {
                        "id": img.id,
                        "filename": img.filename,
                        "original_filename": img.original_filename,
                        "file_size": img.file_size,
                        "mime_type": img.mime_type,
                        "uploaded_at": img.uploaded_at.isoformat() if img.uploaded_at else None,
                        "uploaded_by": img.uploaded_by
                    } for img in wiki_data['images']
                ]
            },
            "status": 200
        })
    
    except Exception as e:
        logger.error(f"Error getting wiki: {e}")
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500

@wiki_bp.route("/api/v1/wiki/<int:wiki_id>", methods=["PUT"])
async def update_wiki(wiki_id: int):
    """Обновить описание wiki"""
    try:
        data = await request.get_json()
        description = data.get('description')
        updated_by = data.get('updated_by', 'anonymous')
        
        # Обрезаем лишние пробелы, но сохраняем переносы строк
        if description:
            # Обрабатываем каждую строку отдельно, чтобы сохранить переносы
            lines = description.strip().split('\n')
            # Убираем лишние пробелы в каждой строке, но сохраняем пустые строки для переносов
            processed_lines = []
            for line in lines:
                processed_lines.append(' '.join(line.split()) if line.strip() else '')
            description = '\n'.join(processed_lines)
        
        if not description:
            return jsonify({
                "error": "Description is required",
                "status": 400
            }), 400
        
        updated_wiki = await WIKI_operation.update_wiki(wiki_id, description, updated_by)
        
        return jsonify({
            "message": "Wiki updated successfully",
            "wiki": {
                "id": updated_wiki.id,
                "description": updated_wiki.description,
                "updated_at": updated_wiki.updated_at.isoformat() if updated_wiki.updated_at else None,
                "created_by": updated_wiki.created_by
            },
            "status": 200
        })
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": 400
        }), 400
    except Exception as e:
        logger.error(f"Error updating wiki: {e}")
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500

@wiki_bp.route("/api/v1/wiki/<int:wiki_id>/images", methods=["POST"])
async def upload_wiki_image(wiki_id: int):
    """Загрузить изображение для wiki"""
    try:
        # Проверяем, существует ли wiki
        wiki = await WIKI_operation.get_wiki_by_id(wiki_id)
        if not wiki:
            return jsonify({
                "error": "Wiki not found",
                "status": 404
            }), 404
        
        # Получаем файл из формы
        if 'image' not in (await request.files):
            return jsonify({
                "error": "No image file provided",
                "status": 400
            }), 400
        
        file = (await request.files)['image']
        uploaded_by = (await request.form).get('uploaded_by', 'anonymous')
        
        if not file.filename:
            return jsonify({
                "error": "No file selected",
                "status": 400
            }), 400
        
        # Загружаем изображение
        wiki_image = await WIKI_operation.upload_wiki_image(wiki_id, file, uploaded_by)
        
        return jsonify({
            "message": "Image uploaded successfully",
            "image": {
                "id": wiki_image.id,
                "filename": wiki_image.filename,
                "original_filename": wiki_image.original_filename,
                "file_size": wiki_image.file_size,
                "mime_type": wiki_image.mime_type,
                "uploaded_at": wiki_image.uploaded_at.isoformat() if wiki_image.uploaded_at else None,
                "uploaded_by": wiki_image.uploaded_by
            },
            "status": 200
        })
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": 400
        }), 400
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500

@wiki_bp.route("/api/v1/wiki/images/<int:image_id>", methods=["DELETE"])
async def delete_wiki_image(image_id: int):
    """Удалить изображение wiki"""
    try:
        success = await WIKI_operation.delete_wiki_image(image_id)
        
        if not success:
            return jsonify({
                "error": "Image not found",
                "status": 404
            }), 404
        
        return jsonify({
            "message": "Image deleted successfully",
            "status": 200
        })
    
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500

@wiki_bp.route("/api/v1/wiki/images/<int:image_id>/file", methods=["GET"])
async def get_wiki_image_file(image_id: int):
    """Получить файл изображения"""
    try:
        # Получаем информацию об изображении
        async with WIKI_operation.async_session() as session:
            from backend.database.database import WikiImage
            from sqlalchemy import select
            
            query = select(WikiImage).where(WikiImage.id == image_id)
            result = await session.execute(query)
            wiki_image = result.scalar_one_or_none()
            
            if not wiki_image:
                return jsonify({
                    "error": "Image not found",
                    "status": 404
                }), 404
            
            # Проверяем существование файла
            if not os.path.exists(wiki_image.file_path):
                return jsonify({
                    "error": "Image file not found",
                    "status": 404
                }), 404
            
            # Отправляем файл
            return await send_file(
                wiki_image.file_path,
                mimetype=wiki_image.mime_type,
                as_attachment=False,
                attachment_filename=wiki_image.original_filename
            )
    
    except Exception as e:
        logger.error(f"Error getting image file: {e}")
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500

@wiki_bp.route("/api/v1/wiki/<int:wiki_id>/images", methods=["GET"])
async def get_wiki_images(wiki_id: int):
    """Получить все изображения для wiki"""
    try:
        images = await WIKI_operation.get_wiki_images(wiki_id)
        
        return jsonify({
            "images": [
                {
                    "id": img.id,
                    "filename": img.filename,
                    "original_filename": img.original_filename,
                    "file_size": img.file_size,
                    "mime_type": img.mime_type,
                    "uploaded_at": img.uploaded_at.isoformat() if img.uploaded_at else None,
                    "uploaded_by": img.uploaded_by
                } for img in images
            ],
            "status": 200
        })
    
    except Exception as e:
        logger.error(f"Error getting wiki images: {e}")
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500
