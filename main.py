import builtins
from flask import Flask, render_template, session, url_for, jsonify
import json

app = Flask(__name__, template_folder="html")

from PIL import Image
from flask import redirect, request, render_template
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv, dotenv_values
from flask_sqlalchemy import SQLAlchemy
import shutil
import requests

app = Flask(__name__, template_folder="html")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:////Users/Nizar/OneDrive - Hogeschool Rotterdam/healthy-cheap2/healthy-cheap/database2.db"
    
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["IMAGES"] = "/Users/Nizar/OneDrive - Hogeschool Rotterdam/healthy-cheap2/healthy-cheap/static/images/"
app.app_context().push()
db = SQLAlchemy()
db.init_app(app)
config = dotenv_values(".env")
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

load_dotenv()


user_key = os.getenv("user_key")


class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column((db.String(100)), nullable=False)
    pass_word = db.Column((db.String(100)), nullable=False)
    img = db.Column((db.String(100)), nullable=False)

    def __init__(self, user_name, pass_word,img):
        self.user_name = user_name
        self.pass_word = pass_word
        self.img = img
    
    def __repr__(self):
        return str(self.img)



@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    image_name = request.files.get("image_name")
   
    if request.method == "POST":
        if image_name.filename == "":
            print("no filename")
            return redirect("/register")
        
        filename = secure_filename(image_name.filename)
        
        

        basedir = os.path.abspath(os.path.dirname(__file__))
        
        
        image_name.save(os.path.join(app.config["IMAGES"]+filename),30 )
        session["filename"] = image_name.filename
        user = users(user_name=username, pass_word=password, img =image_name.filename)
        
        db.session.add(user)
        db.session.commit()
        return render_template(
            "registration.html", user_name=username, pass_word=password,image_name=image_name
        )
    
    if request.method == "GET":
        
        return render_template(
            "registration.html", user_name=username, pass_word=password
        )


@app.route("/login", methods=["GET", "POST"])
def login():
    login_name = request.form.get("login_name")
    login_password = request.form.get("password")
    session["loginname"] = login_name
    
    if request.method == "POST":
        if check_user(login_name, login_password):
            
            return redirect("/nav")

    return render_template(
        "login.html", login_name=login_name, login_password=login_password
    )


def check_user(username, password):
    for i in db.session.query(users):
        print(i.user_name, i.pass_word)
        if i.user_name == username and i.pass_word == password:
            
            session["image"] = i.img
            print(i.img)
            
            return True,i.img
    return False


@app.route("/forum", methods=["GET", "POST"])
def forum():
    forum_page = request.form.get("recipeForm")
    if request.method == "POST":

        return render_template("forum.html", forum_page=forum_page)
    else:
        
        filename = session["image"]
       
    
        loginname = session["loginname"]
        return render_template("forum.html", forum_page=forum_page, loginname =loginname, filename = filename)


@app.route("/kaart", methods=["GET", "POST"])
def map():

    return render_template("kaart.html")

@app.route("/nav", methods=["GET", "POST"])
def nav():

    return render_template("navigate.html")

@app.route("/display_image/<filename>", methods=["GET", "POST"])
def display_image(filename):
       
        return render_template("forum.html", filename =filename)

@app.route("/check")
def check():
    name= "name"
    return {name:"Nizar"}

@app.route("/som")
def som():

    return render_template("something.html")


@app.route("/logout", methods = ["POST","GET"])
def logout():
    session.pop("id",None)
    session.pop("image","not a user")
    print(session)
    
    return redirect("/login")

if __name__ == "__main__":

    db.create_all()
    app.run(debug=True)
