from flask import json

from . import api_blueprint


@api_blueprint.app_errorhandler(404)
def resource_not_found(e):
	response_dict = {"Error": "404 - Resource not found."}
	json_response = json.dumps(response_dict)
	return json_response, 404


@api_blueprint.app_errorhandler(500)
def internal_error(e):
	response_dict = {"Error": "500 - Internal Server Error."}
	json_response = json.dumps(response_dict)
	return json_response, 500
