from flask import Flask
from flask.ext.script import Manager
from db_util import init_db

app = Flask(__name__)
manager = Manager(app)
init_db()

@app.route("/book/<book_id>")
def get_book(book_id):
	book = db_util.get_book(book_id)
	return "Getting book id: " + book.book_name

if __name__ == '__main__':
	manager.run()
