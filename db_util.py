from models import Book
from manage import app
from manage import db

import os


def init_db():
	basedir = os.path.abspath(os.path.dirname(__file__))
	app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
	db.create_all()


def add_book(book_json):
	book = Book(book_name = book_json["book_name"])
	db.session.add(book)
	db.session.commit()

	return book


def get_book(book_id):
	return Book.query.filter_by(id = book_id).first()


def get_books_by_filter(book_name = None):
	query_obj = Book.query
	if book_name is not None:
		query_obj = query_obj.filter_by(book_name = book_name)
	# If more filters, use filter_by again.

	return query_obj.all()


def remove_book(book_id):
	book = get_book(book_id)
	if book is None:
		return None
	db.session.delete(book)
	db.session.commit()

	return book


def update_book(book_id, book_json):
	book = get_book(book_id)
	if book is None:
		return None

	book.book_name = book_json["book_name"]
	db.session.add(book)
	db.session.commit()

	return book


init_db()

