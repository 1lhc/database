# app.py is the main entry point for the application. 
# It creates the Flask app, initializes the database, and registers the API routes. 
# It also configures logging and sets up the Swagger UI.

from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from models import db
from config import Config
import logging

from concurrent.futures import ThreadPoolExecutor
from extensions import cache  # Import from extensions
from routes import api  # Import the blueprint

def create_app():
    app = Flask(__name__)

    # Configure cache
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 3600
    cache.init_app(app)  # Initialize cache with the app

    app.config.from_object(Config)
    app.executor = ThreadPoolExecutor(max_workers=15)
    db.init_app(app)

    # Configure logging
    logging.basicConfig(filename='api.log', level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

    # Root route
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the Work Pass Extension API"})

    # Swagger UI configuration
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Work Pass Extension API"})
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Register API routes
    app.register_blueprint(api, url_prefix='/api')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)