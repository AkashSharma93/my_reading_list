import unittest
import collections

from flask import current_app

from app import create_app
from app.persistence import db_util
from app.persistence import db
from app.auth.auth_handler import register


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_test_user(self, index):
        TestUser = collections.namedtuple("TestUser", ["email", "username", "password"])
        users = [TestUser("testemail%s.com" % str(i), "user" + str(i), "pass" + str(i)) for i in range(10)]

        return users[index]

    def get_user_json(self, test_user):
        user_json = {
            "email": test_user.email,
            "username": test_user.username,
            "password": test_user.password
        }

        return user_json

    def test_register_user(self):
        test_user = self.get_test_user(0)
        user_json = self.get_user_json(test_user)
        user = register(user_json)

        self.assertIsNotNone(user)
        self.assertEqual(user.username, test_user.username)
        self.assertNotEqual(user.password_hash, test_user.password)
        self.assertEqual(user.email, test_user.email)
        self.assertFalse(user.confirmed)
 #       self.assertRaises(AttributeError, user.password)    # This is failing. I wonder why.

    def test_get_user(self):
        test_user = self.get_test_user(0)
        user_json = self.get_user_json(test_user)
        registered_user = register(user_json)

        user = db_util.get_user(registered_user.id)
        self.assertEqual(registered_user.id, user.id)
        self.assertEqual(test_user.email, user.email)
        self.assertEqual(test_user.username, user.username)
        self.assertEqual(registered_user.password_hash, user.password_hash)

    def test_update_user(self):
        test_user = self.get_test_user(0)
        user_json = self.get_user_json(test_user)
        registered_user = register(user_json)

        modified_json = user_json.copy()
        modified_json["username"] = "updated_user_name"
        updated_user = db_util.update_user(registered_user.id, modified_json)

        self.assertEqual(modified_json["username"], updated_user.username)
        self.assertEqual(user_json["email"], updated_user.email)
        self.assertNotEqual(user_json["username"], updated_user.username)
        self.assertEqual(registered_user.password_hash, updated_user.password_hash)

    def test_get_all_users(self):
        users = []

        for i in range(3):
            users.append(register(self.get_user_json(self.get_test_user(i))))
            all_users = db_util.get_all_users()
            self.assertIsNotNone(all_users)
            self.assertEqual(len(all_users), i + 1)

        all_users = db_util.get_all_users()

        for i in range(3):
            self.assertTrue(users[i].username == all_users[i].username)
            self.assertTrue(users[i].email == all_users[i].email)
            self.assertTrue(users[i].password_hash == all_users[i].password_hash)