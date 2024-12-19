import logging

from quart import Blueprint, jsonify, request

from backend.database import Quotes_operation

get_quotes_bp = Blueprint("get_quotes", __name__)
logger = logging.getLogger(__name__)

@get_quotes_bp.route("/api/v1/get_quotes", methods=["GET"])
async def api_get_quotes():
    person_id = request.args.get('person_id', type=int)
    
    if not person_id:
        return jsonify({
            "error": "person_id is required",
            "status": 400
        }), 400
    
    try:
        quotes = await Quotes_operation.get_all_quote_by_person(person_id)
        
        if not quotes:
            return jsonify({
                "error": "No quotes found for this person",
                "status": 404
            }), 404
        
        return jsonify({
            "quotes": [
                {
                    "id": quote.id,
                    "quote": quote.quote,
                    "person_id": quote.person_id
                } for quote in quotes
            ],
            "status": 200
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500
    
@get_quotes_bp.route("/api/v1/get_all_quote", methods=["GET"])
async def api_get_all_quote():
    try:
        quotes = await Quotes_operation.get_all_quote()
        
        if not quotes:
            return jsonify({
                "error": "No quotes found",
                "status": 404
            }), 404
        
        return jsonify({
            "quotes": [
                {
                    "id": quote.id,
                    "quote": quote.quote,
                    "person_id": quote.person_id
                } for quote in quotes
            ],
            "status": 200
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500