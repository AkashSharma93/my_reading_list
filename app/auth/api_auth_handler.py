from flask import request, json, url_for

from . import api_auth, api_auth_blueprint
from ..persistence.models import User
from ..persistence import db_util
import auth_handler


@api_auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if not User:
        return False

    g.current_user = user
    return user.verify_password(password)


@api_auth_blueprint.route("/register", methods=["POST"])
def register():
    request_data = request.get_data()
    if request_data is None or request_data == "":
        return json.dumps(
            {"Error": "JSON data is empty. To register, send POST request with email, username and password."}), 400

    json_data = json.loads(request_data)
    if "email" not in json_data:
        return json.dumps({"Error": "email cannot be empty."}), 400
    if "username" not in json_data:
        return json.dumps({"Error": "username cannot be empty."}), 400
    if "password" not in json_data:
        return json.dumps({"Error": "password cannot be empty."}), 400

    user = auth_handler.register(json_data)
    token = user.generate_confirmation_token()
    user_json = json.dumps({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "url": url_for("api_auth_blueprint.confirm", token=token, _external=True),
        "message": "To confirm your account, send a POST request to the given url, with your email and password."
    })

    return user_json, 200


@api_auth_blueprint.route("/confirm/<token>", methods=["POST"])
def confirm(token):
    request_data = request.get_data()
    if request_data is None or request_data == "":
        return json.dumps(
            {"Error": "JSON data is empty. To register, send POST request with email, username and password."}), 400

    json_data = json.loads(request_data)
    if "email" not in json_data:
        return json.dumps({"Error": "email cannot be empty."}), 400
    if "password" not in json_data:
        return json.dumps({"Error": "password cannot be empty."}), 400

    email = json_data["email"]
    user = db_util.get_user(email=email)
    if user is None:
        return json.dumps({"Error": "User with email id <%s> not found." % email}), 404

    password = json_data["password"]
    if not user.verify_password(password):
        return json.dumps({"Error": "Invalid email or password."}), 401

    if user.confirmed:
        return json.dumps({"message": "You have already verified your account."}), 401

    valid_token = user.confirm(token)
    if valid_token:
        return json.dumps({"message": "You have successfully verified your account."}), 200
    else:
        return json.dumps({"Error": "The token specified is invalid."}), 401
