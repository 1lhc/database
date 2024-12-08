from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from models import db
from config import Config
import logging
from routes import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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
