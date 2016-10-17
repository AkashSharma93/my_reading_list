from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_bootstrap import Bootstrap


app = Flask(__name__)
manager = Manager(app)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)


from data_server import main_blueprint
app.register_blueprint(main_blueprint)

from views import view_blueprint
app.register_blueprint(view_blueprint)


if __name__ == '__main__':
	manager.run()
