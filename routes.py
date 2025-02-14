# Description: This file contains the API routes for the application.

from flask import Blueprint, jsonify, request, current_app
from models import Application, Amendment, STVP, db
from utils import require_api_key
from validation import validate_fin, validate_date  # New import
import logging
from datetime import datetime, date, timedelta
from sqlalchemy import desc, func
from config import Config
from sqlalchemy.orm import Session
import time

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
    
    # Enhanced validation
    if not fin:
        logging.warning("FIN parameter is missing")
        return jsonify({"error": "FIN parameter is required"}), 400
    
    if not validate_fin(fin):
        logging.warning(f"Invalid FIN format: {fin}")
        return jsonify({"error": "Invalid FIN format. Must be 9 characters starting with a letter"}), 400

    try:
        logging.info(f"Searching for applications with FIN: {fin}")
        
        # Database query with explicit error handling
        try:
            applications = Application.query.filter_by(fin=fin).all()
        except Exception as db_error:
            logging.error(f"Database query failed: {str(db_error)}")
            return jsonify({"error": "Database operation failed"}), 500

        logging.info(f"Found {len(applications)} applications")

        if not applications:
            logging.info(f"No applications found for FIN: {fin}")
            return jsonify({"message": "No applications found for the given FIN"}), 404

        # Serialization with error handling
        try:
            result = [{
                "id": app.id,
                "name": app.name,
                "pass_type": app.pass_type,
                "doa": app.doa.isoformat(),
                "doe": app.doe.isoformat(),
                "status": app.status,
                "company_uen": app.company_uen
            } for app in applications]
        except Exception as serialization_error:
            logging.error(f"Data serialization failed: {str(serialization_error)}")
            return jsonify({"error": "Failed to process application data"}), 500

        logging.info(f"Returning {len(result)} applications")
        return jsonify(result)

    except Exception as e:
        logging.error(f"Unexpected error in search: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@api.route('/applications/<string:application_id>/update-expiry', methods=['PUT'])
@require_api_key
def update_expiry(application_id):
    session = Session(db.engine)
    application = session.get(Application, application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    # Check for JSON content
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    new_doe = request.json.get('new_doe')
    if not new_doe:
        return jsonify({"error": "Missing required field: new_doe"}), 400
    
    # Date validation
    if not validate_date(new_doe):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        new_doe = datetime.strptime(new_doe, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date value"}), 400

    try:
        session = Session(db.engine)
        application = session.get(Application, application_id)
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

        return jsonify({
            "message": "Expiry date updated successfully",
            "amendment_id": amendment_id,
            "new_expiry": new_doe.isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Update expiry failed: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to update expiry date"}), 500

@api.route('/applications/<string:application_id>/create-stvp', methods=['POST'])
@require_api_key
def create_stvp(application_id):
    session = Session(db.engine)
    application = session.get(Application, application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    current_date = date.today()
    if application.doe >= current_date:
        return jsonify({"error": "Cannot create STVP for non-expired pass"}), 400

    existing_stvp = STVP.query.filter_by(application_id=application_id).order_by(STVP.end_date.desc()).first()

    if existing_stvp:
        # Update existing STVP
        old_end_date = existing_stvp.end_date
        new_end_date = old_end_date + timedelta(days=30)
        existing_stvp.end_date = new_end_date

        # Log the amendment
        amendment_id = generate_amendment_id(application_id)
        amendment = Amendment(
            amendment_id=amendment_id,
            application_id=application_id,
            original_value=old_end_date.isoformat(),
            amended_value=new_end_date.isoformat()
        )
        db.session.add(amendment)
        db.session.commit()

        return jsonify({
            "message": "Existing STVP extended",
            "stvp_id": existing_stvp.id,
            "new_end_date": new_end_date.isoformat(),
            "amendment_id": amendment_id
        }), 200
    else:
        # Create new STVP
        start_date = max(application.doe, current_date)
        end_date = start_date + timedelta(days=30)
        
        # Generate STVP ID based on application ID
        stvp_id = f"STVP{application_id[1:]}"  # Assuming application_id is in the format 'A0001'
        
        new_stvp = STVP(
            id=stvp_id,
            application_id=application_id,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_stvp)
        db.session.commit()

        return jsonify({
            "message": "New STVP created",
            "stvp_id": stvp_id,
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

from flask import copy_current_request_context
# New endpoint for concurrency testing
@api.route('/test-concurrency', methods=['GET'])
def test_concurrency():
    @copy_current_request_context
    def background_task():
        start = datetime.now()
        logging.info("Started background task")
        try:
            time.sleep(5)  # Simulate a long-running task
            logging.info(f"Task completed in {(datetime.now() - start).total_seconds()}s")
        except Exception as e:
            logging.error(f"Background task failed: {str(e)}")

    # Submit the task to the executor
    future = current_app.executor.submit(background_task)
    return jsonify({
        "message": "Background task started",
        "task_id": str(future)
    }), 202
