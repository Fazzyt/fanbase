import asyncio
import logging

from quart import Quart, render_template, request, redirect

from .database import database, Person_operation, Quotes_operation
from .config import config

app = Quart(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend/templates",
)

logger = logging.getLogger(__name__)


@app.route("/", methods=["get"])
async def main_page():
    person_list = await Person_operation.get_all_person()
    return await render_template("index.html", person_list=person_list)


@app.route("/create_person", methods=["get", "post"])
async def create_person_page():
    if request.method == "POST":
        form = await request.form
        name = form.get("full_name")
        person = await Person_operation.create_person(fullname= name)
        return redirect(f"/{person.full_name}")
    
    return await render_template("create_person.html")


@app.route("/<full_name>", methods=["get"])
async def person_page(full_name):
    person = await Person_operation.get_person_by_name(full_name=full_name)

    if person is None:
        return redirect("/")
    
    quotes = await Quotes_operation.get_all_quote_by_person(person_id=person.id)
    return await render_template("person.html", person=person, quotes=quotes)


@app.route("/<person_id>/create_quotes", methods=["get", "post"])
async def create_quotes_page(person_id):
    if request.method == "POST":
        form = await request.form
        quotes_text = form.get("quotes")
        quotes = await Quotes_operation.create_quote(quote_text=quotes_text, person_id=int(person_id))
        return redirect(f"/")
    
    return await render_template("create_quotes.html",person_id=person_id)


@app.before_serving
async def startup():
    await database.init_db()
    


asyncio.run(
    app.run(host="0.0.0.0", port=config.app_port, debug=config.debug_mode)
)