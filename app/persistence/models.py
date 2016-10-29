from flask import json
from flask import url_for

from . import db


class Book(db.Model):
	__tablename__ = "books"
	id = db.Column(db.Integer, primary_key = True)
	book_name = db.Column(db.String, nullable = False)
	author_name = db.Column(db.String, default="")
	comments = db.Column(db.Text, default="")

	def __repr__(self):
		return "<Book %s>" % self.name

	def to_json(self):
		book_dict = {
			"url": url_for("api_blueprint.get_book", book_id = self.id, _external = True),
			"id": self.id,
			"book_name": self.book_name,
			"author_name": self.author_name,
			"comments": self.comments
		}
		json_data = json.dumps(book_dict)

		return json_data
