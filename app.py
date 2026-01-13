from flask import Flask, render_template, request, redirect, url_for, flash
import os
from data_models import db, Author, Book
from datetime import datetime


app = Flask(__name__)
# key for Flash messages
app.secret_key = "book-alchemy-flash-key"

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data/library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    sort = request.args.get("sort", "title")
    keyword = request.args.get("q", "").strip()

    query = Book.query.join(Author)

    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            db.or_(
                Book.title.ilike(search),
                Author.name.ilike(search)
            )
        )

    if sort == "author":
        books = query.order_by(Author.name).all()
    else:
        books = query.order_by(Book.title).all()

    return render_template("home.html",
                           books=books, sort=sort, keyword=keyword)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name")
        birthdate_str = request.form.get("birthdate")
        death_date_str = request.form.get("date_of_death")

        if not name or name.strip() == "":
            flash("Author name is required.", "danger")
            return render_template("add_author.html")

        birthdate = (
            datetime.strptime(birthdate_str, "%Y-%m-%d").date()
            if birthdate_str else None
        )

        date_of_death = (
            datetime.strptime(death_date_str, "%Y-%m-%d").date()
            if death_date_str else None
        )

        author = Author(
            name=name,
            birth_date=birthdate,
            date_of_death=date_of_death
        )

        db.session.add(author)
        db.session.commit()

        flash(f"Author '{name}' successfully added!", "success")
        return redirect(url_for("add_author"))

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        title = request.form.get("title")
        isbn = request.form.get("isbn")
        publication_year_str = request.form.get("publication_year")
        author_id = int(request.form.get("author_id"))

        publication_year = int(
            publication_year_str) if publication_year_str else None

        book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id
        )

        db.session.add(book)
        db.session.commit()

        flash(f"Book '{title}' successfully added!", "success")
        return redirect(url_for("add_book"))

    return render_template("add_book.html", authors=authors)


if __name__ == "__main__":
    app.run(debug=True, port=5004)
