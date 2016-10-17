from flask import request
from flask import abort
from flask import redirect
from flask import Blueprint


main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/book/<book_id>")
def get_book(book_id):
	book = db_util.get_book(book_id)
	if book is None:
		abort(404)
	return "Getting book: " + book.book_name, 200


@main_blueprint.route("/book", methods = ["POST"])
def add_book():
	data = request.get_json()
	book = db_util.add_book(data)
	return "Book [%s] added successfully." % book.book_name, 200


@main_blueprint.route("/book/<book_id>", methods = ["PUT"])
def update_book(book_id):
	data = request.get_json()
	book = db_util.update_book(book_id, data)
	if book is None:
		abort(404)
	return "Updated book: " + book.book_name, 200


@main_blueprint.route("/book/<book_id>", methods = ["DELETE"])
def delete_book(book_id):
	book = db_util.remove_book(book_id)
	if book is None:
		abort(404)
	return "Deleted book: " + book.book_name, 200


import db_util
