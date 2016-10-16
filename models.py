from manage import db

class Book(db.Model):
	__tablename__ = "books"
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable = False)

	def __repr__(self):
		return "<Book %s>" % self.name