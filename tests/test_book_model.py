import unittest

from flask import current_app

from app import create_app
from app.persistence import db_util
from app.persistence import db


class BookModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_book_json(self, index):
        books = [
            {
                "book_name": "Harry Potter and the Prisoner of Azkaban",
                "author_name": "J K Rowling",
                "comments": "This is the 3rd book in the series."
            },
            {
                "book_name": "Harry Potter and the Philosophers Stone",
                "author_name": "J K Rowling",
            },
            {
                "author_name": "Dan Brown",
                "comments": "This data set has an author but no book name."
            },
            {
                "book_name": "Book with no author.",
                "comments": "Data set with book with no author in it."
            },
            {
                "book_name": "Book with only book name."
            },
            {
                "author_name": "Only author name."
            },
            {
                "comments": "Only comments."
            }
        ]

        return books[index]

    def test_add_book(self):
        book_json = self.get_book_json(0)
        book = db_util.add_book(book_json)
        self.assertTrue(book is not None)
        self.assertTrue(book.book_name == book_json["book_name"])
        self.assertTrue(book.author_name == book_json["author_name"])
        self.assertTrue(book.comments == book_json["comments"])

    def test_get_book(self):
        book_from_get = db_util.get_book(-1)
        self.assertTrue(book_from_get is None)

        book_json = self.get_book_json(0)
        book = db_util.add_book(book_json)
        book_from_get = db_util.get_book(book.id)
        self.assertTrue(book_from_get is not None)
        self.assertTrue(book.book_name == book_from_get.book_name)
        self.assertTrue(book.author_name == book_from_get.author_name)
        self.assertTrue(book.comments == book_from_get.comments)