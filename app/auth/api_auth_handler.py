from flask import request
from flask import json

from . import api_auth
from . import api_auth_blueprint
from ..persistence.models import User
import auth_handler


@api_auth.verify_password
def verify_password(email, password):
	user = User.query.filter_by(email = email).first()
	if not User:
		return False
	
	g.current_user = user
	return user.verify_password(password)


@api_auth_blueprint.route("/register", methods = ["POST"])
def register():
	json_data = request.get_json()
	if "email" not in json_data:
		return json.dumps({"Error": "email cannot be empty."}), 500
	if "username" not in json_data:
		return json.dumps({"Error": "username cannot be empty."}), 500
	if "password" not in json_data:
		return json.dumps({"Error": "password cannot be empty."}), 500

	user = auth_handler.register(json_data)
	user_json = user.to_json()
	print user_json
	return user_json, 200
