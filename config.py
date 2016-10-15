import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	"""
	This class stores all the configuration details required by the application.
	"""

	SECRET_KEY = os.environ.get('SECRET_KEY') or 'Temporary Secret Key value'  # If SECRET_KEY is not set in the environment, then the temporary string will be used.
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True

	@staticmethod
	def init_app(app):
		"""
		This will initialize the application. Leaving it empty for now.
		"""
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "data-dev.sqlite") # Use either the URL provided in the environment or use sqlite file in the project directory.

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "data-test.sqlite")

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "data.sqlite")

config = {
	"development": DevelopmentConfig,
	"testing": TestingConfig,
	"production": ProductionConfig,

	"default": DevelopmentConfig
}