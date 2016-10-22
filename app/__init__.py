from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from config import config
from .ui import bootstrap
from .persistence import db


def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	db.init_app(app)

	# attach routes and custom error pages here
	from .ui import ui_blueprint
	app.register_blueprint(ui_blueprint)
	
	from .api import api_blueprint
	app.register_blueprint(api_blueprint)

	return app
