from flask import Flask, render_template

app = Flask(__name__, template_folder="html")


from flask import redirect, request, render_template

import os
from dotenv import load_dotenv, dotenv_values
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="html")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:////Users/Nizar/OneDrive - Hogeschool Rotterdam/healthy-cheap/database2.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.app_context().push()
db = SQLAlchemy()
db.init_app(app)
config = dotenv_values(".env")

load_dotenv()


user_key = os.getenv("user_key")


class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column((db.String(100)), nullable=False)
    pass_word = db.Column((db.String(100)), nullable=False)

    def __init__(self, user_name, pass_word):
        self.user_name = user_name
        self.pass_word = pass_word


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


@app.route("/login", methods=["GET", "POST"])
def login():
    login_name = request.form.get("login_name")
    login_password = request.form.get("password")

    if request.method == "POST":
        if check_user(login_name, login_password):

            return redirect("/forum")

    return render_template(
        "login.html", login_name=login_name, login_password=login_password
    )


def check_user(username, password):
    for i in db.session.query(users):
        print(i.user_name, i.pass_word)
        if i.user_name == username and i.pass_word == password:
            print(i.user_name, i.pass_word)

            return True
    return False


@app.route("/forum", methods=["GET", "POST"])
def forum():
    forum_page = request.form.get("recipeForm")
    if request.method == "POST":
        return render_template("forum.html", forum_page=forum_page)
    else:
        return render_template("forum.html", forum_page=forum_page)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
