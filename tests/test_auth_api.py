import unittest

from flask import url_for, json

from app import create_app
from app.persistence import db, db_util


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

    def test_register_api_no_json_data(self):
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

    def test_register_api_no_email(self):
        # Check response when incomplete json data is sent. [Email absent]
        request_data = json.dumps({
            "username": "test_user",
            "password": "test_password"
        })
        response = self.client.post(url_for("api_auth_blueprint.register"), data=request_data)
        self.assertEqual(response.status_code, 400)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(data["Error"], "email cannot be empty.")

    def test_register_api_no_username(self):
        # Check response when incomplete json data is sent. [Username absent]
        request_data = json.dumps({
            "email": "test_email@123.com",
            "password": "test_password"
        })
        response = self.client.post(url_for("api_auth_blueprint.register"), data=request_data)
        self.assertEqual(response.status_code, 400)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(data["Error"], "username cannot be empty.")

    def test_register_api_no_password(self):
        # Check response when incomplete json data is sent. [Password absent]
        request_data = json.dumps({
            "email": "test_email@123.com",
            "username": "test_user"
        })
        response = self.client.post(url_for("api_auth_blueprint.register"), data=request_data)
        self.assertEqual(response.status_code, 400)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(data["Error"], "password cannot be empty.")

    def test_register_api(self):
        request_dict = {
            "email": "test_email@email.com",
            "username": "test_username",
            "password": "test_password"
        }
        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.register"), data=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        for key in ("id", "email", "username", "url", "message", "token"):
            self.assertIn(key, data)

        self.assertEqual(data["username"], request_dict["username"])
        self.assertEqual(data["email"], request_dict["email"])
        self.assertEqual(data["message"],
                         "To confirm your account, send a POST request to the given url, with your email and password.")

    def test_confirm_api_no_json_data(self):
        response = self.client.get(url_for("api_auth_blueprint.confirm", token="1234"))
        self.assertEqual(response.status_code, 405)

        # Empty POST request data.
        response = self.client.post(url_for("api_auth_blueprint.confirm", token="1234"))
        self.assertEqual(response.status_code, 400)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertEqual(data["Error"],
                         "JSON data is empty. To register, send POST request with email, username and password.")

    def test_confirm_api_no_password(self):
        # Check response when incomplete json data is sent. [password absent]
        request_data = json.dumps({
            "email": "test_email@email.com"
        })
        response = self.client.post(url_for("api_auth_blueprint.confirm", token="1234"), data=request_data)
        self.assertEqual(response.status_code, 400)
        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertEqual(data["Error"], "password cannot be empty.")

    def test_confirm_api_no_email(self):
        # Check response when incomplete json data is sent. [email absent]
        request_data = json.dumps({
            "password": "test_password"
        })
        response = self.client.post(url_for("api_auth_blueprint.confirm", token="1234"), data=request_data)
        self.assertEqual(response.status_code, 400)
        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertEqual(data["Error"], "email cannot be empty.")

    def test_confirm_api_unregistered_email(self):
        # Check response when unregistered email is provided.
        request_data = json.dumps({
            "email": "test_email@gmail.com",
            "password": "test_password"
        })
        response = self.client.post(url_for("api_auth_blueprint.confirm", token="1234"), data=request_data)
        self.assertEqual(response.status_code, 404)
        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertEqual(data["Error"], "User with email <%s> not found." % "test_email@gmail.com")

    def test_confirm_api_invalid_password(self):
        # Check response when password is invalid.
        request_dict = {
            "email": "test_email@email.com",
            "username": "test_username",
            "password": "test_password"
        }
        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.register"), data=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)

        token = data["token"]
        request_dict["password"] = "wrong_password"
        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.confirm", token=token), data=request_data)
        self.assertEqual(response.status_code, 401)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertEqual(data["Error"], "Invalid email or password.")

    def test_confirm_api_confirm_registration(self):
        # Check response when successful confirmation is done.
        request_dict = {
            "email": "test_email@email.com",
            "username": "test_username",
            "password": "test_password"
        }
        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.register"), data=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)

        token = data["token"]
        registered_user = db_util.get_user(data["id"])
        self.assertFalse(registered_user.confirmed)

        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.confirm", token=token), data=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "You have successfully verified your account.")

        self.assertTrue(registered_user.confirmed)

    def test_confirm_api_reconfirm(self):
        # Check response when successful confirmation is done, and confirmation is tried again.
        request_dict = {
            "email": "test_email@email.com",
            "username": "test_username",
            "password": "test_password"
        }
        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.register"), data=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)

        token = data["token"]
        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.confirm", token=token), data=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "You have successfully verified your account.")

        # Sending confirmation request again.
        response = self.client.post(url_for("api_auth_blueprint.confirm", token=token), data=request_data)
        self.assertEqual(response.status_code, 401)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "You have already verified your account.")

    def test_confirm_api_invalid_token(self):
        # Check response when token is invalid
        request_dict = {
            "email": "test_email@email.com",
            "username": "test_username",
            "password": "test_password"
        }
        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.register"), data=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)

        token = data["token"]
        registered_user = db_util.get_user(data["id"])
        request_data = json.dumps(request_dict)
        response = self.client.post(url_for("api_auth_blueprint.confirm", token="1234"), data=request_data)
        self.assertEqual(response.status_code, 401)

        data = response.get_data(as_text=True)
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertEqual(data["Error"], "The token specified is invalid.")
        self.assertFalse(registered_user.confirmed)