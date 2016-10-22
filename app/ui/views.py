from flask import Blueprint
from flask import render_template

from . import ui_blueprint


@ui_blueprint.route("/index")
def index():
	return render_template("index.html"), 200

@ui_blueprint.route("/book/<book_id>")
def show_book_details(book_id):
	return render_template("book_details.html"), 200
