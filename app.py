from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from models import db
from config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Configure logging
logging.basicConfig(filename='api.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Work Pass Extension API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)

from flask import jsonify, request
from models import Application
from utils import require_api_key

@app.route('/applications/search', methods=['GET'])
@require_api_key
def search_applications():
    fin = request.args.get('fin')
    if not fin:
        return jsonify({"error": "FIN parameter is required"}), 400
    
    applications = Application.query.filter_by(fin=fin).all()
    return jsonify([{
        "id": app.id,
        "name": app.name,
        "pass_type": app.pass_type,
        "doa": app.doa,
        "doe": app.doe,
        "status": app.status
    } for app in applications])
