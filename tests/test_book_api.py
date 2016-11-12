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
        for key in ("book_name", "author_name", "comments", "id", "url"):
            self.assertIn(key, data)
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
        for key in ("book_name", "author_name", "comments", "url", "id"):
            self.assertIn(key, data)
        self.assertTrue(book_data.book_name, data["book_name"])
        self.assertTrue(book_data.author_name, data["author_name"])
        self.assertTrue(book_data.comments, data["comments"])

    def test_post_book_bookname_absent(self):
        # Check response when a book without book_name is added.
        book_dict = self.get_book_dict(self.get_book_data(0))
        del book_dict["book_name"]
        book_json = json.dumps(book_dict)

        response = self.client.post(url_for("api_blueprint.add_book"), data=book_json)
        self.assertTrue(response.status_code, 400)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertTrue(data["Error"], "book_name cannot be absent.")

    def test_update_book_no_json(self):
        # Check response when a book update is requested without json data.
        response = self.client.put(url_for("api_blueprint.update_book", book_id=123))
        self.assertEqual(response.status_code, 400)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertIn("Error", data)
        self.assertTrue(data["Error"],
                        "JSON data is empty. To update book, send PUT request with book_name, [author_name] and [comments].")

    def test_update_book_non_existent(self):
        # Check response when trying to update a book which doesn't exist.
        book_json = json.dumps(self.get_book_dict(self.get_book_data(0)))
        response = self.client.put(url_for("api_blueprint.update_book", book_id=123), data=book_json)
        self.assertEqual(response.status_code, 404)

    def test_update_book_book_name(self):
        # Check response when trying to update only the book_name.
        book_data = self.get_book_data(0)
        book_dict = self.get_book_dict(book_data)
        book_json = json.dumps(book_dict)
        response = self.client.post(url_for("api_blueprint.add_book"), data=book_json)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())

        # Update book.
        book_dict["book_name"] = "Updated book name"
        book_json = json.dumps(book_dict)
        response = self.client.put(url_for("api_blueprint.update_book", book_id=data["id"]), data=book_json)
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(book_data.author_name, data["author_name"])
        self.assertEqual(book_data.comments, data["comments"])
        self.assertEqual(book_dict["book_name"], data["book_name"])
        self.assertNotEqual(book_data.book_name, data["book_name"])

    def test_update_book_author_name(self):
        # Check response when trying to update only the author_name.
        book_data = self.get_book_data(0)
        book_dict = self.get_book_dict(book_data)
        book_json = json.dumps(book_dict)
        response = self.client.post(url_for("api_blueprint.add_book"), data=book_json)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())

        # Update book.
        book_dict["author_name"] = "Updated author name"
        book_json = json.dumps(book_dict)
        response = self.client.put(url_for("api_blueprint.update_book", book_id=data["id"]), data=book_json)
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(book_data.book_name, data["book_name"])
        self.assertEqual(book_data.comments, data["comments"])
        self.assertEqual(book_dict["author_name"], data["author_name"])
        self.assertNotEqual(book_data.author_name, data["author_name"])

    def test_update_book_comments(self):
        # Check response when trying to update only the comments.
        book_data = self.get_book_data(0)
        book_dict = self.get_book_dict(book_data)
        book_json = json.dumps(book_dict)
        response = self.client.post(url_for("api_blueprint.add_book"), data=book_json)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())

        # Update book.
        book_dict["comments"] = "Updated comments."
        book_json = json.dumps(book_dict)
        response = self.client.put(url_for("api_blueprint.update_book", book_id=data["id"]), data=book_json)
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(book_data.book_name, data["book_name"])
        self.assertEqual(book_data.author_name, data["author_name"])
        self.assertEqual(book_dict["comments"], data["comments"])
        self.assertNotEqual(book_data.comments, data["comments"])

    def test_update_book_all_attributes(self):
        # Check response when trying to update all the attributes of a book.
        book_data = self.get_book_data(0)
        book_dict = self.get_book_dict(book_data)
        book_json = json.dumps(book_dict)
        response = self.client.post(url_for("api_blueprint.add_book"), data=book_json)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())

        # Update book.
        book_dict["book_name"]  = "Updated book name"
        book_dict["author_name"] = "Updated author name"
        book_dict["comments"] = "Updated comments."
        book_json = json.dumps(book_dict)
        response = self.client.put(url_for("api_blueprint.update_book", book_id=data["id"]), data=book_json)
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(book_dict["book_name"], data["book_name"])
        self.assertNotEqual(book_data.book_name, data["book_name"])
        self.assertEqual(book_dict["author_name"], data["author_name"])
        self.assertNotEqual(book_data.author_name, data["author_name"])
        self.assertEqual(book_dict["comments"], data["comments"])
        self.assertNotEqual(book_data.comments, data["comments"])

    def test_delete_all_books(self):
        # Check response when all books are tried to be deleted.
        for i in range(3):
            db_util.add_book(self.get_book_dict(self.get_book_data(i)))

        response = self.client.delete("/api/books")
        self.assertEqual(response.status_code, 405)

    def test_delete_book_non_existent(self):
        # Check response when a non-existent book is tried to be deleted.
        response = self.client.delete(url_for("api_blueprint.delete_book", book_id=123))
        self.assertEqual(response.status_code, 404)

    def test_delete_exiting_book(self):
        # Check response when an existing book is deleted.
        book_data = self.get_book_data(0)
        book_dict = self.get_book_dict(book_data)
        added_book = db_util.add_book(book_dict)

        response = self.client.delete(url_for("api_blueprint.delete_book", book_id=added_book.id))
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIsNotNone(data)
        data = json.loads(data)
        self.assertEqual(added_book.book_name, data["book_name"])
        self.assertEqual(added_book.author_name, data["author_name"])
        self.assertEqual(added_book.comments, data["comments"])

        # Check if the book has actually been deleted.
        response = self.client.delete(url_for("api_blueprint.get_book", book_id=added_book.id))
        self.assertEqual(response.status_code, 404)

        # Add and delete multiple books just to be sure.
        books = [db_util.add_book(self.get_book_dict(self.get_book_data(i))) for i in range(3)]

        for i in range(3):
            response = self.client.delete(url_for("api_blueprint.delete_book", book_id=books[i].id))
            self.assertTrue(response.status_code, 200)