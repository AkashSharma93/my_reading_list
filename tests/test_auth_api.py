import unittest

from flask import url_for, json

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

    def test_register_api(self):
        response = self.client.get(url_for("api_auth_blueprint.register"))
        self.assertEqual(response.status_code, 405)

        # Check response when no json data is sent.
        response = self.client.post(url_for("api_auth_blueprint.register"))
        self.assertEqual(response.status_code, 400)
        data = response.get_data()
        self.assertIsNotNone(data)

        data = json.loads(data)
        self.assertTrue("Error" in data)
        self.assertEqual(data["Error"],
                         "JSON data is empty. To register, send POST request with email, username and password.")

        # Check response when incomplete json data is sent.
        response = self.client.post(url_for("api_auth_blueprint.register"), data={
            "username": "test_user",
            "password": "test_password"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        data = response.get_data(as_text=True)
        data = json.loads(data)
        self.assertEqual(data["Error"], "email cannot be empty.")