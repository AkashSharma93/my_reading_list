from flask import Blueprint
from flask_bootstrap import Bootstrap


bootstrap = Bootstrap()
ui_blueprint = Blueprint('ui_blueprint', __name__)


from . import views, errors
