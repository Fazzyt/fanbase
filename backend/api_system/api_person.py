import logging

from quart import Blueprint, jsonify, request

from backend.database import Person_operation

get_person_bp = Blueprint("get_person", __name__)
logger = logging.getLogger(__name__)

@get_person_bp.route("/api/v1/get_person", methods=["GET"])
async def api_get_person():
    full_name = request.args.get('full_name', type=str)
    person_id = request.args.get('person_id', type=int)
    
    if not full_name and not person_id:
        return jsonify({
            "error": "full_name or person_id is required",
            "status": 400
        }), 400
    
    try:
        if full_name:
            person = await Person_operation.get_person_by_name(full_name)
        if person_id:
            person = await Person_operation.get_person_by_id(person_id)

        if not person:
            return jsonify({
                "error": "No found person",
                "status": 404
            }), 404
        
        return jsonify({
            "person": [
                {
                    "id": person.id,
                    "full_name": person.full_name
                }
            ],
            "status": 200
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": 500
        }), 500
