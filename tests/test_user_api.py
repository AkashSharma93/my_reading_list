import unittest
import collections

from flask import url_for, json

from app import create_app
from app.persistence import db_util
from app.persistence import db
from app.auth import auth_handler


class UserAPITestCase(unittest.TestCase):
    TestUser = collections.namedtuple("TestUser", ["username", "email", "password"])
    users = [TestUser("username_" + str(i), "email_" + str(i), "password_" + str(i)) for i in range(10)]

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

    def get_user_data(self, index):
        return UserAPITestCase.users[index]

    def get_user_dict(self, user_data):
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "password": user_data.password
        }
        return user_dict

    def test_get_all_users(self):
        # Check the response for get all users.
        users = [auth_handler.register(self.get_user_dict(self.get_user_data(i))) for i in range(5)]
        response = self.client.get(url_for("api_blueprint.get_all_users"))
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        for index, user_json in enumerate(data["users"]):
            user = json.loads(user_json)
            self.assertEqual(users[index].id, user["id"])
            self.assertEqual(users[index].username, user["username"])
            self.assertEqual(users[index].email, user["email"])

    def test_get_user_non_exitent(self):
        # Check the response when a get_user on a non-existent user is performed.
        response = self.client.get(url_for("api_blueprint.get_user", user_id=123))
        self.assertEqual(response.status_code, 404)

    def test_get_existent_user(self):
        # Check response of get_user for existing user.
        user_data = self.get_user_data(0)
        user_dict = self.get_user_dict(user_data)
        registered_user = auth_handler.register(user_dict)
        response = self.client.get(url_for("api_blueprint.get_user", user_id=registered_user.id))
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        for key in ("url", "id", "email", "username", "confirmed"):
            self.assertIn(key, data)

        self.assertEqual(registered_user.id, data["id"])
        self.assertEqual(registered_user.username, data["username"])
        self.assertEqual(registered_user.email, data["email"])
        self.assertEqual(registered_user.confirmed, data["confirmed"])

    def test_update_user_non_existent(self):
        # Check response while updating a non-existent user.
        user_json = json.dumps(self.get_user_dict(self.get_user_data(0)))
        response = self.client.put(url_for("api_blueprint.update_user", user_id=123), data=user_json)
        self.assertEqual(response.status_code, 404)

    def test_update_user_no_json(self):
        # Check response of update_user when no json is provided.
        response = self.client.put(url_for("api_blueprint.update_user", user_id=123))
        self.assertEqual(response.status_code, 400)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertEqual(data["Error"],
                        "JSON data is empty. To update user, send PUT request with username, [email] and [password].")