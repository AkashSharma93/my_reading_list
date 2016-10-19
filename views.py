from flask import Blueprint
from flask import render_template


view_blueprint = Blueprint("views", __name__)


@view_blueprint.route("/index")
def index():
	return render_template("index.html"), 200

@view_blueprint.route("/book/<book_id>")
def show_book_details(book_id):
	return render_template("book_details.html"), 200
