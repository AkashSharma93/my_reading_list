from flask import request, abort, redirect, json

from . import api_blueprint
from ..persistence import db_util


@api_blueprint.route("/api/books/<int:book_id>")
def get_book(book_id):
	book = db_util.get_book(book_id)
	if book is None:
		abort(404)
	
	#Temporary solution
	json_data = book.to_json()
	return json_data, 200


@api_blueprint.route("/api/books", methods = ["POST"])
def add_book():
	data = request.get_json()
	book = db_util.add_book(data)
	json_data = book.to_json()
	return json_data, 200


@api_blueprint.route("/api/books/<int:book_id>", methods = ["PUT"])
def update_book(book_id):
	data = request.get_json()
	book = db_util.update_book(book_id, data)
	if book is None:
		abort(404)
	
	json_data = book.to_json()
	return json_data, 200


@api_blueprint.route("/api/books/<int:book_id>", methods = ["DELETE"])
def delete_book(book_id):
	book = db_util.remove_book(book_id)
	if book is None:
		abort(404)

	json_data = book.to_json()
	return json_data, 200


@api_blueprint.route("/api/books", methods = ["GET"])
def get_all_books():
	books = db_util.get_all_books()
	books_dict = {
		"books": [book.to_json() for book in books]
	}
	json_data = json.dumps(books_dict)

	return json_data, 200
