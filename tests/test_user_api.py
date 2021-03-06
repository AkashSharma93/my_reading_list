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
        users = [UserAPITestCase.register_and_confirm(self, self.get_user_dict(self.get_user_data(i))) for i in range(5)]
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
        user_dict = self.get_user_dict(self.get_user_data(0))
        registered_user = UserAPITestCase.register_and_confirm(self, user_dict)
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

    def test_update_user_username(self):
        # Test udpate_user with only username
        user_data = self.get_user_data(0)
        user_dict = self.get_user_dict(user_data)
        registered_user_dict = UserAPITestCase.register_user(self, user_dict)
        registered_user = db_util.get_user(registered_user_dict["id"])
        confirmed = registered_user.confirmed

        # Update user.
        user_dict["username"] = "Updated username"
        response = self.client.put(url_for("api_blueprint.update_user", user_id=registered_user.id),
                                   data=json.dumps(user_dict))
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(user_data.email, data["email"])
        self.assertEqual(confirmed, data["confirmed"])
        self.assertEqual(user_dict["username"], data["username"])
        self.assertNotEqual(user_data.username, data["username"])

    def test_update_user_email(self):
        # Test udpate_user with only email
        user_data = self.get_user_data(0)
        user_dict = self.get_user_dict(user_data)
        registered_user_dict = UserAPITestCase.register_user(self, user_dict)
        registered_user = db_util.get_user(registered_user_dict["id"])
        confirmed = registered_user.confirmed

        # Update user.
        user_dict["email"] = "Updated email"
        response = self.client.put(url_for("api_blueprint.update_user", user_id=registered_user.id),
                                   data=json.dumps(user_dict))
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(user_data.username, data["username"])
        self.assertEqual(confirmed, data["confirmed"])
        self.assertEqual(user_dict["email"], data["email"])
        self.assertNotEqual(user_data.email, data["email"])

    def test_update_user_all_attributes(self):
        # Test udpate_user with all attributes.
        user_data = self.get_user_data(0)
        user_dict = self.get_user_dict(user_data)
        registered_user_dict = UserAPITestCase.register_user(self, user_dict)
        registered_user = db_util.get_user(registered_user_dict["id"])
        confirmed = registered_user.confirmed

        # Update user.
        user_dict["email"] = "Updated email"
        user_dict["username"] = "Updated username"
        response = self.client.put(url_for("api_blueprint.update_user", user_id=registered_user.id),
                                   data=json.dumps(user_dict))
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(confirmed, data["confirmed"])
        self.assertEqual(user_dict["email"], data["email"])
        self.assertNotEqual(user_data.email, data["email"])
        self.assertEqual(user_dict["username"], data["username"])
        self.assertNotEqual(user_data.username, data["username"])

    def test_update_user_password(self):
        # Test password update.
        user_data = self.get_user_data(0)
        user_dict = self.get_user_dict(user_data)
        registered_user = UserAPITestCase.register_and_confirm(self, user_dict)

        # Change password.
        user_dict["password"] = "Updated_password"
        response = self.client.put(url_for("api_blueprint.update_user", user_id=registered_user.id),
                                   data=json.dumps(user_dict))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())

        # Verify the new token in response.
        self.assertIn("token", data)
        token = data["token"]
        self.assertNotEqual(token, "")

        # Confirm account again.
        response = self.client.post(url_for("api_auth_blueprint.confirm", token=token), data=json.dumps(user_dict))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "You have successfully verified your account.")

    def test_delete_user_non_existent(self):
        # Test delete API on a non-existent user.
        response = self.client.delete(url_for("api_blueprint.delete_user", user_id=123))
        self.assertEqual(response.status_code, 404)

    def test_delete_existing_user(self):
        # Test delete API on existing user.
        user_data = self.get_user_data(0)
        user_dict = self.get_user_dict(user_data)
        registered_user = UserAPITestCase.register_and_confirm(self, user_dict)

        response = self.client.delete(url_for("api_blueprint.delete_user", user_id=registered_user.id))
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(user_data.username, data["username"])
        self.assertEqual(user_data.email, data["email"])
        self.assertEqual(registered_user.id, data["id"])
        response = self.client.get(url_for("api_blueprint.get_user", user_id=registered_user.id))
        self.assertEqual(response.status_code, 404)

        # Add and delete multiple users.
        users = [UserAPITestCase.register_and_confirm(self, self.get_user_dict(self.get_user_data(i))) for i in range(3)]

        for i in range(3):
            response = self.client.delete(url_for("api_blueprint.delete_user", user_id=users[i].id))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(db_util.get_all_users()), (3 - i) - 1)

    def test_delete_all_users(self):
        # Check response of delete all users.
        response = self.client.delete("/api/users")
        self.assertEqual(response.status_code, 405)

    @staticmethod
    def register_user(test_obj, user_dict):
        # Helper function to register a user.
        response = test_obj.client.post(url_for("api_auth_blueprint.register"), data=json.dumps(user_dict))
        test_obj.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        test_obj.assertIsNotNone(data)
        data = json.loads(data)
        for key in ("id", "email", "username", "url", "message", "token"):
            test_obj.assertIn(key, data)

        test_obj.assertEqual(data["username"], user_dict["username"])
        test_obj.assertEqual(data["email"], user_dict["email"])
        test_obj.assertEqual(data["message"],
                             "To confirm your account, send a POST request to the given url, with your email and password.")

        registered_user = db_util.get_user(data["id"])
        test_obj.assertFalse(registered_user.confirmed)

        return data

    @staticmethod
    def register_and_confirm(test_obj, user_dict):
        # Helper function to register a user AND confirm the user.
        data = UserAPITestCase.register_user(test_obj, user_dict)
        registered_user = db_util.get_user(data["id"])
        token = data["token"]

        response = test_obj.client.post(url_for("api_auth_blueprint.confirm", token=token), data=json.dumps(user_dict))
        test_obj.assertEqual(response.status_code, 200)

        data = response.get_data(as_text=True)
        test_obj.assertIsNotNone(data)
        data = json.loads(data)
        test_obj.assertIn("message", data)
        test_obj.assertEqual(data["message"], "You have successfully verified your account.")
        test_obj.assertTrue(registered_user.confirmed)

        return registered_user
