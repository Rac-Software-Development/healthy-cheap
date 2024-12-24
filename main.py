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
    post= db.relationship("posts", backref=db.backref("users", lazy=True))

    def __init__(self, user_name, pass_word,img):
        self.user_name = user_name
        self.pass_word = pass_word
        self.img = img
        return self.id
    
    def __repr__(self):
        return f"({self.user_name}, {self.img})"
    
    
   




class posts(db.Model):
    __tablename__= "posts"
    post_id = db.Column(db.Integer, primary_key=True )
    price = db.Column((db.Float(100)), nullable=False)
    ingredients = db.Column((db.String(100)), nullable=False)
    dish = db.Column((db.String(100)), nullable=False)

    users_id = db.Column(db.Integer, db.ForeignKey("users.id"))
   
    user = db.relationship("users", backref=db.backref("posts", lazy=True))


    def __init__(self,price,ingredients,dish,user_id):
        self.users_id = user_id
        self.price = price
        self.ingredients = ingredients
        self.dish = dish
    
    def __repr__(self):
        return f"('{self.post_id}', '{self.dish}','{self.price},{self.users_id}')"



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
            
            session["id"] = i.id
            session["image"] = i.img
            print(i.img,session)
            
            return True,i.img
    return False


@app.route("/forum", methods=["GET", "POST"])
def forum():
   
    price = request.form.get("price")
    ingredients = request.form.get("ingredients")
    dish = request.form.get("dish")
    if 'id' in session:
        if request.method == "POST":
            post_of_user = posts(price=price,ingredients=ingredients,dish=dish,user_id=session['id'])
        
            db.session.add(post_of_user)
            db.session.commit()

            return render_template("forum.html",price = price,ingredients=ingredients,dish=dish )
        else:
            
            filename = session["image"]
        
        
            loginname = session["loginname"]
            return render_template("forum.html",  loginname =loginname, filename = filename)
    else:
        return redirect("/login")


@app.route("/kaart", methods=["GET", "POST"])
def map():
       
        if 'id' in session:
        

            return render_template("kaart.html")
        else:
            print(session)
            return redirect("/login")
    

@app.route("/nav", methods=["GET", "POST"])
def nav():
    if 'id' in session:
        return render_template("navigate.html")
    else:
        return redirect("/login")

@app.route("/display_image/<filename>", methods=["GET", "POST"])
def display_image(filename):
       
        return render_template("forum.html", filename =filename)

@app.route("/check", methods=["POST","GET"])
def check():
    

    if request.method == "POST":
        return {"name":"John"}
    if request.method == "GET":
        my_posts = posts.query.all()
        print(my_posts)
        user = users.query.all()
        print(u for u in user)
        # for u in user:
        #     u
        #     return {"name":str(u)}

        return {"name":[str(u) for u in user]}
        
        
        # return  {"name":session["loginname"],"image":session["image"],"post":[str(post) for post in my_posts ]}
        
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
