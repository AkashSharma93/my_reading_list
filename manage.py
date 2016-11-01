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

COV = None
if os.environ.get("FLASK_COVERAGE"):
    import coverage

    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()


@manager.command
def test(coverage=False):
    if coverage and not os.environ.get("FLASK_COVERAGE"):
        import sys
        os.environ["FLASK_COVERAGE"] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print("Coverage summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, "tmp/coverage")
        COV.html_report(directory=covdir)
        print "HTML version: file://%s/index.html" % covdir
        COV.erase()


@manager.command
def setup_db():
    from app.persistence.db_util import init_db
    init_db()


if __name__ == '__main__':
    manager.run()
