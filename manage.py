import os

from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db


app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command("db", MigrateCommand)


@manager.command
def test():
	import unittest
	tests = unittest.TestLoader().discover("tests")
	unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def setup_db():
	from app.persistence.db_util import init_db
	init_db()


if __name__ == '__main__':
	manager.run()
