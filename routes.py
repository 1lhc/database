from flask import Blueprint, jsonify, request
from models import Application, db
from utils import require_api_key

search_applications = Blueprint('search_applications', __name__)

@search_applications.route('/applications/search', methods=['GET'])
@require_api_key
def search():
    fin = request.args.get('fin')
    if not fin:
        return jsonify({"error": "FIN parameter is required"}), 400
    
    try:
        applications = Application.query.filter_by(fin=fin).all()
        return jsonify([{
            "id": app.id,
            "name": app.name,
            "pass_type": app.pass_type,
            "doa": app.doa,
            "doe": app.doe,
            "status": app.status
        } for app in applications])
    except Exception as e:
        return jsonify({"error": "An error occurred while searching for applications", "details": str(e)}), 500