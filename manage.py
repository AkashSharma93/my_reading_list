from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager

app = Flask(__name__)
manager = Manager(app)
db = SQLAlchemy(app)

from DataServer import main_blueprint
app.register_blueprint(main_blueprint)

if __name__ == '__main__':
	manager.run()