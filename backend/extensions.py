"""Extension objects for the Flask application.

This module holds the shared extension instances so they can be imported
elsewhere without causing circular imports.
"""

from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect

jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()
