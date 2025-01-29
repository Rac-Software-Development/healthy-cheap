from base64 import encodebytes
import builtins
import io
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
        return f"('{self.ingredients}', '{self.dish}','{self.price},{self.users_id}')"

class reactions(db.Model):
    __tablename__ = "reactions"
    id = db.Column(db.Integer, primary_key=True )
    reaction = db.Column((db.String(100)), nullable=False)
    users_id_2= db.Column(db.Integer, db.ForeignKey("users.id"))

    user = db.relationship("users", backref=db.backref("reactions", lazy=True))
    posts_id= db.Column(db.Integer, db.ForeignKey("posts.post_id"))

    post = db.relationship("posts", backref=db.backref("reactions", lazy=True))

    def __init__(self,reaction,users_id_2,posts_id):
        self.users_id_2 = users_id_2
        self.reaction = reaction
        self.posts_id = posts_id
    
    def __repr__(self):
        return f"('{self.users_id_2}', '{self.reaction}',{self.posts_id})"

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
            print(session)
        
            loginname = session["loginname"]
            return render_template("forum.html",  loginname =loginname, filename = filename)
    else:
        return redirect("/login")


@app.route("/forum_reaction",methods = ["GET","POST"])
def forum_reaction():
    reaction = request.form.get("reaction")
    if 'id' in session:
        if request.method == "POST":
            print(session)
            reaction_on_post = reactions(reaction=reaction,users_id_2=session["id"])
            
            db.session.add(reaction_on_post)
            db.session.commit()
            return render_template("forum.html",reaction=reaction)
        else:
            return render_template("forum.html",reaction=reaction)
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




@app.route("/logout", methods = ["POST","GET"])
def logout():
    session.pop("id",None)
   
    print(session)
    
    return redirect("/login")



@app.route("/check", methods=["POST","GET"])
def check():
    

    if request.method == "POST":
        return {"name":"John"}
    if request.method == "GET":
        my_posts = posts.query.all()
        all_users = users.query.all()

        users_list = []
        for g in all_users:
            users_list.append(str(g.img))
            users_list.append(int(g.id))
            users_list.append(str(g.user_name))
           
        

        user_dict = {}
        user_dict["user_image"] = [i for i in users_list]
        user_dict["user_name"] = [i for i in users_list]
        
        user_dict["user_id"] = [i for i in users_list  if type(i) == int]
        print(user_dict)

        # for t in user_dict["user_image"]:
            
        #         user_dict["üser_image"] = [list(k)+[k] for i in user_dict["user_image"]]
     
        new_dict = {}
        

        posts_list = []
        for p in my_posts:
         
            posts_list.append((p.users_id,p.price,p.dish,p.ingredients,p.post_id))
            

 

        posts_dict = {}
        posts_dict["user"]= posts_list[0]
        
            
        new_list = []
        for i in range(0,len(users_list),3):
            pair = users_list[i:i + 3] 
            new_list.append(pair) 

        for t,k in enumerate(new_list):
            
            
          
                print(t)
                for i,worth in enumerate(posts_list):
                    for v,d in enumerate(new_list):
                        if d[1] == worth[0]:
                            
                                l = list(worth) +d
                                posts_list[i]= l
                        
                            
                user_post = {"name": session['loginname'],"post": posts_list}
                                    
                                        
                return user_post
                        
        return {"name":"error"}
    
@app.route("/info/<event_id>", methods=["GET"])
def info(event_id):
    posts1 = posts.query.all()
    event_id = posts1
    return render_template("information.html",event_id=event_id)
                
            
@app.route("/react", methods=["GET"])
def react():
    my_reactions = reactions.query.all()
    all_users = users.query.all()

    users_list = []
    for g in all_users:
        users_list.append(str(g.img))
        users_list.append(int(g.id))
        users_list.append(str(g.user_name))




    new_list = []
    for i in range(0,len(users_list),3):
            pair = users_list[i:i + 3] 
            new_list.append(pair) 

    react_list = []
    for i in my_reactions:
        react_list.append(i.users_id_2)
        react_list.append(i.reaction)
        # react_list.append(i.posts_id)

    
    react2_list = []
    for i in range(0,len(react_list),2):
            pair = react_list[i:i + 2] 
            react2_list.append(pair)

  
    for i,worth in enumerate(react2_list):
        for v,d in enumerate(new_list):
            if d[1] == worth[0]:
                
                    l = list(worth) +d
                    react_list[i]= l
                    if type(i) != list:
                        react_list.pop()

    return {"reaction":react_list}
                        

    
price:int = ["sdfsdf",4,5,6]
print(type(price))



if __name__ == "__main__":

    db.create_all()
    app.run(debug=True)
