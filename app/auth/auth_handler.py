from . import auth_blueprint


@auth_blueprint.route("/login")
def login():
	return "You are in login route now."
