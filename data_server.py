from flask import request
from flask import abort
from flask import Blueprint


main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/book/<book_id>")
def get_book(book_id):
	book = db_util.get_book(book_id)
	if book is None:
		abort(404)
	return "Getting book id: " + book.book_name


@main_blueprint.route("/book", methods = ["POST"])
def add_book():
	data = request.get_json()
	return data["book_name"]


import db_util
