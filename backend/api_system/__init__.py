__all__ = ["api_system_bp", "api_person", "api_quotes"]

from quart import Blueprint

from . import api_person, api_quotes

api_system_bp = Blueprint("api", __name__)

api_system_bp.register_blueprint(api_person.get_person_bp)
api_system_bp.register_blueprint(api_quotes.get_quotes_bp)
