import asyncio
import logging
import hashlib

from quart import Quart, render_template, request, redirect, url_for, jsonify

from .database import database, Person_operation, Quotes_operation, WIKI_operation
from .config import config
from .api_system import api_system_bp

app = Quart(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend/templates",
)

logger = logging.getLogger(__name__)

app.register_blueprint(api_system_bp)

@app.route("/", methods=["get", "post"])
async def main_page():
    if request.method == "POST":
        form = await request.form
        name = form.get("full_name")
        person = await Person_operation.create_person(fullname= name)
        return redirect(f"/{person.full_name}")

    person_list = await Person_operation.get_all_person()
    for person in person_list:
        person.quote_count = await Quotes_operation.get_quote_count_by_person(person.id)
    return await render_template("index.html", person_list=person_list)

@app.route("/<full_name>", methods=["get", "post"])
async def person_page(full_name):
    person = await Person_operation.get_person_by_name(full_name=full_name)

    if person is None:
        return redirect("/")
    
    if request.method == "POST":
        form = await request.form
        quotes_text = form.get("quotes")
        quotes = await Quotes_operation.create_quote(quote_text=quotes_text, person_id=person.id)
        return redirect(f"/{person.full_name}")
    
    quotes = await Quotes_operation.get_all_quote_by_person(person_id=person.id)
    return await render_template("person.html", person=person, quotes=quotes)

@app.route("/wiki/<full_name>", methods=["get", "post"])
async def wiki_person_page(full_name):
    person = await Person_operation.get_person_by_name(full_name=full_name)

    if person is None:
        return redirect("/")
    
    if request.method == "POST":
        form = await request.form
        description = form.get("description")
        
        # Обрезаем лишние пробелы, но сохраняем переносы строк
        if description:
            # Обрабатываем каждую строку отдельно, чтобы сохранить переносы
            lines = description.strip().split('\n')
            # Убираем лишние пробелы в каждой строке, но сохраняем пустые строки для переносов
            processed_lines = []
            for line in lines:
                processed_lines.append(' '.join(line.split()) if line.strip() else '')
            description = '\n'.join(processed_lines)
        
        # Проверяем, существует ли уже wiki для этого человека
        existing_wiki = await WIKI_operation.get_wiki_by_teacher_id(person_id=person.id)
        
        if existing_wiki:
            # Обновляем существующую wiki
            wiki = await WIKI_operation.update_wiki(existing_wiki[0].id, description, "user")
        else:
            # Создаем новую wiki
            wiki = await WIKI_operation.create_wiki(description, person.id, "user")
        
        return redirect(f"/wiki/{person.full_name}")
    
    wiki_list = await WIKI_operation.get_wiki_by_teacher_id(person_id=person.id)
    wiki_obj = wiki_list[0] if wiki_list else None
    
    # Получаем изображения если wiki существует
    if wiki_obj:
        wiki_with_images = await WIKI_operation.get_wiki_with_images(wiki_obj.id)
        if wiki_with_images:
            # Создаем простой объект с данными wiki и изображениями
            class SimpleWiki:
                def __init__(self, data):
                    self.id = data['id']
                    self.person_id = data['person_id']
                    self.description = data['description']
                    # Преобразуем даты в строки для безопасного отображения
                    if data['created_at']:
                        if hasattr(data['created_at'], 'strftime'):
                            self.created_at = data['created_at'].strftime('%d.%m.%Y %H:%M')
                        else:
                            self.created_at = str(data['created_at'])
                    else:
                        self.created_at = None
                    
                    if data['updated_at']:
                        if hasattr(data['updated_at'], 'strftime'):
                            self.updated_at = data['updated_at'].strftime('%d.%m.%Y %H:%M')
                        else:
                            self.updated_at = str(data['updated_at'])
                    else:
                        self.updated_at = None
                    
                    self.created_by = data['created_by']
                    self.images = data['images']
            
            wiki = SimpleWiki(wiki_with_images)
        else:
            # Если нет изображений, создаем простой объект
            class SimpleWiki:
                def __init__(self, wiki_obj):
                    self.id = wiki_obj.id
                    self.person_id = wiki_obj.person_id
                    self.description = wiki_obj.description
                    self.created_at = getattr(wiki_obj, 'created_at', None)
                    self.updated_at = getattr(wiki_obj, 'updated_at', None)
                    self.created_by = getattr(wiki_obj, 'created_by', None)
                    self.images = []
            
            wiki = SimpleWiki(wiki_obj)
    else:
        wiki = None
    
    return await render_template("wiki_person.html", person=person, wiki=wiki)

@app.route('/edit_quote/<int:quote_id>', methods=['POST'])
async def edit_quote(quote_id):
    form = await request.form
    new_quote_text = form.get('quote_text')

    quote = await Quotes_operation.update_quote(quote_id, new_quote_text)

    person = await Person_operation.get_person_by_id(quote.person_id)

    return redirect(f"/{person.full_name}")

@app.route("/admin/<password>", methods=["get", "post"])
async def admin_page(password):
    if hashlib.sha3_512(password.encode()).hexdigest() != config.admin_password:
        return redirect("/")
    
    if request.method == "POST":
        form = await request.form
        person_id = form.get("person_id")
        new_name = form.get("new_name")

        delete_quote_id = form.get("delete_quote_id")
        delete_person_id = form.get("delete_person_id")

        if person_id and new_name:
            await Person_operation.update_person(int(person_id), new_name)
        if delete_person_id:
            await Person_operation.delete_person(int(delete_person_id))
        if delete_quote_id:
            await Quotes_operation.delete_quote(int(delete_quote_id))

    return await render_template("admin.html")

@app.route("/about", methods=["get"])
async def about_page():
    return await render_template("about.html")   


@app.before_serving
async def startup():
    await database.init_db()

asyncio.run(
    app.run(host="0.0.0.0", port=config.app_port, debug=config.debug_mode)
)