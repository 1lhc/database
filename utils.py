from functools import wraps
from flask import request, jsonify
from config import Config
import logging

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if Config.REQUIRE_API_KEY:
            if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == Config.API_KEY:
                return f(*args, **kwargs)
            else:
                logging.warning('Unauthorized access attempt')
                return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
