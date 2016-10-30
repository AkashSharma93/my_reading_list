from . import ui_auth_blueprint


@ui_auth_blueprint.route("/login")
def login():
	return "You are in login route now."
