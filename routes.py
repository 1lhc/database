from flask import Blueprint, jsonify, request
from models import Application, db
from utils import require_api_key
import logging

search_applications = Blueprint('search_applications', __name__)

@search_applications.route('/applications/search', methods=['GET'])
@require_api_key
def search():
    fin = request.args.get('fin')
    if not fin:
        logging.warning("FIN parameter is missing")
        return jsonify({"error": "FIN parameter is required"}), 400

    
    try:
        logging.info(f"Searching for applications with FIN: {fin}")
        applications = Application.query.filter_by(fin=fin).all()
        logging.info(f"Found {len(applications)} applications")

        if not applications:
            logging.info(f"No applications found for FIN: {fin}")
            return jsonify({"message": "No applications found for the given FIN"}), 404

        result = [{
            "id": app.id,
            "name": app.name,
            "pass_type": app.pass_type,
            "doa": app.doa,
            "doe": app.doe,
            "status": app.status
        } for app in applications]

        logging.info(f"Returning {len(result)} applications")
        return jsonify(result)
    except Exception as e:
        logging.error(f"An error occurred while searching for applications: {str(e)}")
        return jsonify({"error": "An error occurred while searching for applications", "details": str(e)}), 500