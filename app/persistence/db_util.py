import os

from .models import Book, User
from . import db


def init_db():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db.create_all()


def drop_tables():
    db.drop_all()


def add_book(book_json):
    book = Book(book_name=book_json["book_name"])
    if "author_name" in book_json:
        book.author_name = book_json["author_name"]
    if "comments" in book_json:
        book.comments = book_json["comments"]

    db.session.add(book)
    db.session.commit()

    return book


def get_book(book_id):
    return Book.query.filter_by(id=book_id).first()


def get_all_books():
    return Book.query.all()


def get_books_by_filter(book_name=None, author_name=None):
    query_obj = Book.query
    if book_name is not None:
        query_obj = query_obj.filter_by(book_name=book_name)
    # If more filters, use filter_by again.
    if author_name is not None:
        query_obj = query_obj.filter_by(author_name=author_name)

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

    if "book_name" in book_json:
        book.book_name = book_json["book_name"]
    if "author_name" in book_json:
        book.author_name = book_json["author_name"]
    if "comments" in book_json:
        book.comments = book_json["comments"]

    db.session.add(book)
    db.session.commit()

    return book


def get_user(user_id):
    return User.query.filter_by(id=user_id).first()


def get_all_users():
    return User.query.all()


def get_users_by_filter(username=None, email=None):
    query_obj = User.query
    if username is not None:
        query_obj = query_obj.filter_by(username=username)
    # If more filters, use filter_by again.
    if email is not None:
        query_obj = query_obj.filter_by(email=email)

    return query_obj.all()


def remove_user(user_id):
    user = get_user(user_id)
    if user is None:
        return None
    db.session.delete(user)
    db.session.commit()

    return user


def update_user(user_id, user_json):
    user = get_user(user_id)
    if user is None:
        return None

    if "username" in user_json:
        user.username = user_json["username"]
    if "email" in user_json:
        user.email = user_json["email"]
    if "password" in user_json:
        # Requires re-confirmation of account.
        user.password = user_json["password"]
        user.confirmed = False

    db.session.add(user)
    db.session.commit()

    return user
