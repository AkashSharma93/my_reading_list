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
                "book_name": "Inferno",
                "author_name": "Dan Brown",
                "comments": "Latest Dan Brown book."
            },
            {
                "book_name": "To Kill a Mocking Bird",
                "author_name": "Harper Lee",
                "comments": "A pretty awesome book!!"
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

    def test_get_all_books(self):
        books = []
        books.append(db_util.add_book(self.get_book_json(0)))
        all_books = db_util.get_all_books()

        self.assertTrue(all_books is not None)
        self.assertTrue(len(all_books) == 1)

        books.append(db_util.add_book(self.get_book_json(1)))
        all_books = db_util.get_all_books()
        self.assertTrue(len(all_books) == 2)

        books.append(db_util.add_book(self.get_book_json(2)))
        all_books = db_util.get_all_books()
        self.assertTrue(len(all_books) == 3)

        for i in range(3):
            self.assertTrue(books[i].book_name == all_books[i].book_name)
            self.assertTrue(books[i].author_name == all_books[i].author_name)
            self.assertTrue(books[i].comments == all_books[i].comments)

    def test_remove_book(self):
        org_book = db_util.add_book(self.get_book_json(0))
        org_book_2 = db_util.add_book(self.get_book_json(1))

        book = db_util.remove_book(org_book.id)
        self.assertTrue(book.book_name == org_book.book_name)
        self.assertTrue(book.author_name == org_book.author_name)
        self.assertTrue(book.comments == org_book.comments)
        self.assertTrue(len(db_util.get_all_books()) == 1)

        db_util.remove_book(org_book_2.id)
        self.assertTrue(len(db_util.get_all_books()) == 0)

    def test_update_book_comments(self):
        book_json = self.get_book_json(0)

        # Modifying only the comments.
        modified_json = book_json.copy()
        modified_json["comments"] = "This is the updated comment!"

        org_book = db_util.add_book(book_json)
        updated_book = db_util.update_book(org_book.id, modified_json)

        self.assertTrue(book_json["comments"] != updated_book.comments)
        self.assertTrue(book_json["book_name"] == updated_book.book_name)
        self.assertTrue(book_json["author_name"] == updated_book.author_name)

    def test_update_book_bookname(self):
        book_json = self.get_book_json(0)

        # Modifying only the book name.
        modified_json = book_json.copy()
        modified_json["book_name"] = "New book name"

        org_book = db_util.add_book(book_json)
        updated_book = db_util.update_book(org_book.id, modified_json)

        self.assertTrue(book_json["book_name"] != updated_book.book_name)
        self.assertTrue(book_json["comments"] == updated_book.comments)
        self.assertTrue(book_json["author_name"] == updated_book.author_name)

    def test_update_book_authorname(self):
        book_json = self.get_book_json(0)

        # Modifying only the author name.
        modified_json = book_json.copy()
        modified_json["author_name"] = "New author name"

        org_book = db_util.add_book(book_json)
        updated_book = db_util.update_book(org_book.id, modified_json)

        self.assertTrue(book_json["book_name"] == updated_book.book_name)
        self.assertTrue(book_json["comments"] == updated_book.comments)
        self.assertTrue(book_json["author_name"] != updated_book.author_name)

    def test_update_book_all(self):
        book_json = self.get_book_json(0)

        # Modifying all the attributes.
        modified_json = book_json.copy()
        modified_json["author_name"] = "New author name"
        modified_json["book_name"] = "New book name"
        modified_json["comments"] = "Updated comments."

        org_book = db_util.add_book(book_json)
        updated_book = db_util.update_book(org_book.id, modified_json)

        self.assertTrue(book_json["book_name"] != updated_book.book_name)
        self.assertTrue(book_json["comments"] != updated_book.comments)
        self.assertTrue(book_json["author_name"] != updated_book.author_name)

    def test_bookname_unique_constraint(self):
        # Check the response when two books with same name are added to the DB.
        book_json = self.get_book_json(0)
        db_util.add_book(book_json)
        book_json["author"] = "somethingelse"
        book_json["comments"] = "some other comment."

        unique_constraint_raised = False
        try:
            db_util.add_book(book_json)
        except:
            unique_constraint_raised = True

        self.assertTrue(unique_constraint_raised)

    def test_get_book_by_filter_no_filter(self):
        # Check response of get_book_by_filter if no filters are specified. [Should return all books]
        for i in range(3):
            db_util.add_book(self.get_book_json(i))

        self.assertEqual(db_util.get_all_books(), db_util.get_books_by_filter())

    def test_get_book_by_filter_book_name(self):
        # Check response of get_book_by_filter when the book's name is provided.
        pass