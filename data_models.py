from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    books = db.relationship("Book", backref="author",
                            cascade="all, delete", lazy=True)

    def __str__(self):
        return f"Author(id={self.id}, name={self.name})"


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)
    rating = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey(
        'authors.id'), nullable=False)

    def __str__(self):
        return f"Book(id={self.id}, title={self.title})"

    @property
    def cover_url(self):
        if self.isbn:
            return f"https://covers.openlibrary.org/b/isbn/{self.isbn}-M.jpg"
        return "/static/no-cover.png"
