from flask import json
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Book(db.Model):
	__tablename__ = "books"
	id = db.Column(db.Integer, primary_key = True)
	book_name = db.Column(db.String, nullable = False, unique = True, index = True)
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


class User(UserMixin, db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String, unique = True, index = True)
	username = db.Column(db.Integer, unique = True, index = True)
	password_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError("password is not a readable attribute.")
	
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def __repr__(self):
		return "<User %s>" % self.username

	def to_json(self):
		user_dict = {
			"id": self.id,
			"email": self.email,
			"username": self.username,
		}
		json_data = json.dumps(user_dict)

		return json_data
