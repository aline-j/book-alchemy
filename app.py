from flask import Flask, render_template, request, redirect, url_for, flash
import os
from data_models import db, Author
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


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name")
        birthdate_str = request.form.get("birthdate")
        death_date_str = request.form.get("date_of_death")

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


if __name__ == "__main__":
    app.run(debug=True, port=5004)
