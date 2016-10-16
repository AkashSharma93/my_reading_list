from flask import request
from flask import Blueprint
from manage import app

main_blueprint = Blueprint("main", __name__)

import db_util
@main_blueprint.route("/book/<book_id>")
def get_book(book_id):
	book = db_util.get_book(book_id)
	return "Getting book id: " + book.book_name

@main_blueprint.route("/book", methods = ["POST"])
def add_book():
	return request.data