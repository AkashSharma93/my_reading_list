from flask import request, abort, redirect, json

from . import api_blueprint
from ..persistence import db_util


@api_blueprint.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db_util.get_book(book_id)
    if book is None:
        abort(404)

    json_data = book.to_json()
    return json_data, 200


@api_blueprint.route("/books", methods=["POST"])
def add_book():
    request_data = request.get_data()
    if request_data is None or request_data == "":
        return json.dumps({
            "Error": "JSON data is empty. To add book, send POST request with book_name, [author_name] and [comments]."
        }), 400

    data = json.loads(request_data)
    if "book_name" not in data:
        return json.dumps({"Error": "book_name cannot be empty."}), 400

    book = db_util.add_book(data)
    json_data = book.to_json()
    return json_data, 200


@api_blueprint.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    request_data = request.get_data()
    if request_data is None or request_data == "":
        return json.dumps(
            {"Error": "JSON data is empty. To update book, send PUT request with book_name, [author_name] and [comments]."}), 400

    data = json.loads(request_data)
    book = db_util.update_book(book_id, data)
    if book is None:
        abort(404)

    json_data = book.to_json()
    return json_data, 200


@api_blueprint.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db_util.remove_book(book_id)
    if book is None:
        abort(404)

    json_data = book.to_json()
    return json_data, 200


@api_blueprint.route("/books", methods=["GET"])
def get_all_books():
    books = db_util.get_all_books()
    books_dict = {
        "books": [book.to_json() for book in books]
    }
    json_data = json.dumps(books_dict)

    return json_data, 200


@api_blueprint.route("/users", methods=["GET"])
def get_all_users():
    users = db_util.get_all_users()
    users_dict = {
        "users": [user.to_json() for user in users]
    }
    json_data = json.dumps(users_dict)

    return json_data, 200


@api_blueprint.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db_util.get_user(user_id)
    if user is None:
        abort(404)

    json_data = user.to_json()
    return json_data, 200


@api_blueprint.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    request_data = request.get_data()
    if request_data is None or request_data == "":
        return json.dumps({
            "Error": "JSON data is empty. To update user, send PUT request with username, [email] and [password]."
        }), 400

    data = json.loads(request_data)
    user = db_util.update_user(user_id, data)
    if user is None:
        abort(404)

    json_data = user.to_json()
    return json_data, 200


@api_blueprint.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db_util.remove_user(user_id)
    if user is None:
        abort(404)

    json_data = user.to_json()
    return json_data, 200
