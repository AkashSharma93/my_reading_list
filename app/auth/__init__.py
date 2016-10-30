from flask import Blueprint
from flask_httpauth import HTTPBasicAuth


ui_auth_blueprint = Blueprint("ui_auth_blueprint", __name__)
api_auth_blueprint = Blueprint("api_auth_blueprint", __name__)
api_auth = HTTPBasicAuth()


from . import auth_handler, api_auth_handler, ui_auth_handler
