import unittest
import collections

from flask import url_for, json

from app import create_app
from app.persistence import db_util
from app.persistence import db


class BookAPITestCase(unittest.TestCase):
    TestBook = collections.namedtuple("TestBook", ["book_name", "author_name", "comments"])
    books = [TestBook("book_name_" + str(i), "author_name_" + str(i), "comments_" + str(i)) for i in range(10)]

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

    def get_book_data(self, index):
        return BookAPITestCase.books[index]

    def get_book_dict(self, book_data):
        book_dict = {
            "book_name": book_data.book_name,
            "author_name": book_data.author_name,
            "comments": book_data.comments
        }
        return book_dict

    def test_get_book_api_non_existant_book(self):
        # Check response when non-existant book is requested.
        response = self.client.get(url_for("api_blueprint.get_book", book_id=123))
        self.assertEqual(response.status_code, 404)

    def test_get_book_that_exists(self):
        # Check response when a book that exists is requested.
        book_data = self.get_book_data(0)
        book_dict = self.get_book_dict(book_data)
        added_book = db_util.add_book(book_dict)

        response = self.client.get(url_for("api_blueprint.get_book", book_id=added_book.id))
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(data["book_name"], added_book.book_name)
        self.assertEqual(data["author_name"], added_book.author_name)
        self.assertEqual(data["comments"], added_book.comments)

    def test_post_book_no_json(self):
        # Check response when no request json is sent to POST book API.
        response = self.client.post(url_for("api_blueprint.add_book"))
        self.assertEqual(response.status_code, 400)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(data["Error"],
                         "JSON data is empty. To add book, send POST request with book_name, [author_name] and [comments].")

    def test_post_book_add_book(self):
        # Check response when a book is added.
        book_data = self.get_book_data(0)
        book_dict = self.get_book_dict(book_data)
        book_json = json.dumps(book_dict)

        response = self.client.post(url_for("api_blueprint.add_book"), data=book_json)
        self.assertTrue(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertTrue(book_data.book_name, data["book_name"])
        self.assertTrue(book_data.author_name, data["author_name"])
        self.assertTrue(book_data.comments, data["comments"])