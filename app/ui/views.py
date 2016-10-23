from flask import Blueprint, render_template, url_for
import requests

from . import ui_blueprint


@ui_blueprint.route("/index")
def index():
	response = requests.get(url_for("api_blueprint.get_all_books", _external = True))
	return render_template("index.html", books = books), 200

@ui_blueprint.route("/book/<book_id>")
def show_book_details(book_id):
	return render_template("book_details.html"), 200
