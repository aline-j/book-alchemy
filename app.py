from flask import Flask, render_template, request, redirect, url_for, flash
import os
from data_models import db, Author, Book
from datetime import datetime
from sqlalchemy.exc import IntegrityError


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
        name = request.form.get("name", "").strip()
        birthdate_str = request.form.get("birthdate")
        death_date_str = request.form.get("date_of_death")

        if not name:
            flash("Author name is required.", "danger")
            return render_template("add_author.html")

        # 🔎 1. Vorher prüfen
        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:
            flash("An author with this name already exists.", "danger")
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

        try:
            db.session.add(author)
            db.session.commit()
            flash(f"Author '{name}' successfully added!", "success")
            return redirect(url_for("add_author"))

        except IntegrityError:
            db.session.rollback()
            flash("An author with this name already exists.", "danger")

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        title = request.form.get("title")
        isbn = request.form.get("isbn") or None
        publication_year_str = request.form.get("publication_year")
        author_id = int(request.form.get("author_id"))
        rating_str = request.form.get("rating")

        publication_year = int(
            publication_year_str) if publication_year_str else None
        rating = int(rating_str) if rating_str else None

        if isbn and Book.query.filter_by(isbn=isbn).first():
            flash("A book with this ISBN already exists.", "danger")
            return render_template("add_book.html", authors=authors)

        isbn = isbn.replace("-", "").strip() if isbn else None

        book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id,
            rating=rating
        )

        try:
            db.session.add(book)
            db.session.commit()
            flash(f"Book '{title}' successfully added!", "success")
            return redirect(url_for("add_book"))

        except IntegrityError:
            db.session.rollback()
            flash("A book with this ISBN already exists.", "danger")

    return render_template("add_book.html", authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    db.session.delete(book)
    db.session.commit()
    flash(f"Book '{book.title}' successfully deleted!", "success")

    return redirect(url_for("home"))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)

    author_name = author.name

    db.session.delete(author)
    db.session.commit()

    flash(
        f"Author '{author_name}' and all related books were"
        f"deleted successfully.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5004)
