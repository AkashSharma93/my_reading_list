import unittest

from flask import url_for

from app import create_app
from app.persistence import db


class AuthApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_basic_api_call(self):
        response = self.client.get(url_for("api_auth_blueprint.register"))
        self.assertIsNotNone(response)
