from flask import Flask, render_template

app = Flask(__name__, template_folder="html")


from flask import redirect, request, render_template, Flask

import os

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="html")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:////Users/Nizar/OneDrive - Hogeschool Rotterdam/healthy-cheap/database2.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.app_context().push()
db = SQLAlchemy()
db.init_app(app)


user_key = os.getenv("user_key")


class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column((db.String(100)), nullable=False)
    pass_word = db.Column((db.String(100)), nullable=False)

    def __init__(self, user_name, pass_word):
        self.user_name = user_name
        self.pass_word = pass_word
        return f"{self.user_name},{ self.pass_word}"


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if request.method == "POST":

        user = users(user_name=username, pass_word=password)
        db.session.add(user)
        db.session.commit()
        return render_template(
            "registration.html", user_name=username, pass_word=password
        )
    if request.method == "GET":
        return render_template(
            "registration.html", user_name=username, pass_word=password
        )


if __name__ == "__main__":
    app.run(debug=True)
