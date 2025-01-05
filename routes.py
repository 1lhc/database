# Description: This file contains the API routes for the application.

from flask import Blueprint, jsonify, request
from models import Application, Amendment, STVP, db
from utils import require_api_key
import logging
from datetime import datetime, date, timedelta
from sqlalchemy import desc, func
from config import Config
import uuid

api = Blueprint('api', __name__)

def generate_amendment_id(application_id):
    # Get the count of existing amendments for this application
    count = Amendment.query.filter_by(application_id=application_id).count()
    # Increment the count and format the amendment ID
    return f'P{(count + 1):02d}{application_id}'


@api.route('/applications/search', methods=['GET'])
@require_api_key
def search_applications():
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
            "doa": app.doa.isoformat(),
            "doe": app.doe.isoformat(),
            "status": app.status,
            "company_uen": app.company_uen
        } for app in applications]

        logging.info(f"Returning {len(result)} applications")
        return jsonify(result)
    except Exception as e:
        logging.error(f"An error occurred while searching for applications: {str(e)}")
        return jsonify({"error": "An error occurred while searching for applications"}), 500

@api.route('/applications/<string:application_id>/update-expiry', methods=['PUT'])
@require_api_key
def update_expiry(application_id):
    new_doe = request.json.get('new_doe')
    if not new_doe:
        return jsonify({"error": "New date of expiry (new_doe) is required"}), 400

    try:
        new_doe = datetime.strptime(new_doe, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    application = Application.query.get(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    if application.doe < datetime.now().date():
        return jsonify({"error": "Cannot update expired application"}), 400

    old_doe = application.doe
    application.doe = new_doe

    amendment_id = generate_amendment_id(application_id)
    amendment = Amendment(
        amendment_id=amendment_id,
        application_id=application_id,
        original_value=old_doe.isoformat(),
        amended_value=new_doe.isoformat()
    )

    db.session.add(amendment)
    db.session.commit()

    return jsonify({"message": "Expiry date updated successfully", "amendment_id": amendment_id}), 200

@api.route('/applications/<string:application_id>/create-stvp', methods=['POST'])
@require_api_key
def create_stvp(application_id):
    application = Application.query.get(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    current_date = date.today()
    if application.doe >= current_date:
        return jsonify({"error": "Cannot create STVP for non-expired pass"}), 400

    existing_stvp = STVP.query.filter_by(application_id=application_id).order_by(STVP.end_date.desc()).first()

    if existing_stvp and existing_stvp.end_date >= current_date:
        # Extend existing STVP
        old_end_date = existing_stvp.end_date
        existing_stvp.end_date = old_end_date + timedelta(days=30)
        db.session.commit()
        return jsonify({
            "message": "Existing STVP extended",
            "new_end_date": existing_stvp.end_date.isoformat()
        }), 200

    # Create new STVP
    start_date = max(application.doe, current_date)
    end_date = start_date + timedelta(days=30)
    new_stvp = STVP(
        id=str(uuid.uuid4()),  # Generate a unique ID for the STVP
        application_id=application_id,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(new_stvp)
    db.session.commit()

    return jsonify({
        "message": "New STVP created",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }), 201

@api.route('/applications', methods=['GET'])
@require_api_key
def list_applications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', Config.ITEMS_PER_PAGE, type=int)

    applications = Application.query.paginate(page=page, per_page=per_page, error_out=False)

    if not applications.items:
        return jsonify({"message": "No applications found"}), 404

    result = [{
        "id": app.id,
        "name": app.name,
        "pass_type": app.pass_type,
        "doa": app.doa.isoformat(),
        "doe": app.doe.isoformat(),
        "status": app.status
    } for app in applications.items]

    return jsonify({
        "applications": result,
        "total": applications.total,
        "pages": applications.pages,
        "current_page": page
    })

@api.route('/applications/<string:application_id>/amendments', methods=['GET'])
@require_api_key
def get_amendment_history(application_id):
    amendments = Amendment.query.filter_by(application_id=application_id).order_by(Amendment.amendment_date).all()

    if not amendments:
        return jsonify({"message": "No amendments found for this application"}), 404

    result = [{
        "amendment_id": amendment.amendment_id,
        "amendment_date": amendment.amendment_date.isoformat(),
        "original_value": amendment.original_value,
        "amended_value": amendment.amended_value
    } for amendment in amendments]

    return jsonify(result)
