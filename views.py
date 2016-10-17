from flask import Blueprint
from flask import render_template


view_blueprint = Blueprint("views", __name__)


@view_blueprint.route("/index")
def index():
	return render_template("index.html"), 200
