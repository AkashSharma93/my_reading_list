from manage import app

@app.route("/book/<book_id>")
def get_book(book_id):
	book = db_util.get_book(book_id)
	return "Getting book id: " + book.book_name