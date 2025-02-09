# utils.py
# The require_api_key decorator is used to protect API routes that require an API key for access.

from functools import wraps
from flask import request, jsonify
from config import Config
import logging
from flask_limiter import Limiter

limiter = Limiter(key_func=lambda: request.headers.get('X-API-Key'))

def require_api_key(f):
    @wraps(f)
    @limiter.limit("10/minute")
    def decorated(*args, **kwargs):
        if Config.REQUIRE_API_KEY:
            if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == Config.API_KEY:
                return f(*args, **kwargs)
            else:
                logging.warning('Unauthorized access attempt')
                return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
