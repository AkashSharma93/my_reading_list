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
        self.assertTrue(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        for index, user_json in enumerate(data["users"]):
            user = json.loads(user_json)
            self.assertEqual(users[index].id, user["id"])
            self.assertEqual(users[index].username, user["username"])
            self.assertEqual(users[index].email, user["email"])