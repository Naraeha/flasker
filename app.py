from sqlite3 import DataError, DatabaseError
from xml.sax.handler import property_declaration_handler
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Create a flask instance
app = Flask(__name__)

# Create a CKEditor instance
ckeditor = CKEditor(app)

# Add database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# sql
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# mysql://username:password@localhost/db_name
#app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:freeto753@localhost/our_users'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://ilblfxjfbunwqc:041ad37ea611794423c41dbd5df5e909aeaac3dfb0c44cff355947ad9d0afe09@ec2-18-215-41-121.compute-1.amazonaws.com:5432/d2r08g4le4mqaq'

# Secret key
app.config["SECRET_KEY"] = "secret key"

UPLOAD_FOLDER = "static/images/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#Initialize The database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)


# Flask Login system
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


#-----------------------------------------------------------------------------------------------------------
#Add Post Page
@app.route("/add-post", methods=["GET", "POST"])
#@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     slug=form.slug.data,
                     poster_id=poster)
        # Clear the form
        form.title.data = ""
        form.content.data = ""
        #form.author.data = ""
        form.slug.data = ""

        # Add post to the database
        db.session.add(post)
        db.session.commit()
        
        # Return a message
        flash("Blog Post Submitted Successfully.")

    # redirect to the webpage
    return render_template("add_post.html", form=form)

#-----------------------------------------------------------------------------------------------------------

@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    # validate
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.favorite_color.data = ""
        form.password_hash.data = ""
        flash("User Added Successfully.")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           name=name,
                           form=form,
                           our_users=our_users)

#-----------------------------------------------------------------------------------------------------------

# Create Admin Page
@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == 14:
        return render_template("admin.html")
    else:
        flash("Acces Denied - Admin Status Required.")
        return redirect(url_for("dashboard"))

#-----------------------------------------------------------------------------------------------------------

# Create Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.usernamme = request.form["username"]
        name_to_update.about_author = request.form["about_author"]
        name_to_update.profile_pic = request.files["profile_pic"]
        
        # Grab Image Name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        #Set uuid
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        

        # Save the Image
        saver =  request.files["profile_pic"]
        

        # Change it to a string save to db
        name_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            saver.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_name))
            flash("User updated Successfully.")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error - Something went wrong in updating the database.")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
    else:
         return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)

#-----------------------------------------------------------------------------------------------------------

# Delete records from database
@app.route("/delete/<int:id>")
def delete(id):
    name = None
    form = UserForm()
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully.")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
                           name=name,
                           form=form,
                           our_users=our_users)
    except:
        flash("Error - Something went wrong deleting the User.")
        return render_template("add_user.html",
                           name=name,
                           form=form,
                           our_users=our_users)

#-----------------------------------------------------------------------------------------------------------

@app.route("/posts/delete/<int:id>")
@login_required
def delete_post(id):
    post_delete = Posts.query.get_or_404(id)
    id = current_user.id

    if id == post_delete.poster.id:
        try:
            db.session.delete(post_delete)
            db.session.commit()
            flash("Post deleted successfully.")
        
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html",
                                    posts=posts)
                          
        except:
            flash("Error - Something went wrong deleting Post.")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html",
                                    posts=posts)
    else:
        flash("You Aren't Authorized To Delete This Post.")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",
                                posts=posts)
#-----------------------------------------------------------------------------------------------------------

@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
  
    if form.validate_on_submit():
        post.title = form.title.data
        #post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        db.session.add(post)
        db.session.commit()
        flash("Post has been updated.")
        return redirect(url_for("post", id=post.id))
   
    if current_user.id == post.poster_id:
        form.title.data = post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("edit.html", form=form)
    else:
        flash("You Aren't Authorized To Edit This Post.")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",
                                posts=posts)


#-----------------------------------------------------------------------------------------------------------

# Create Json
@app.route("/date")
def get_current_date():
    favorite_pizza= {"Naraeha": "Pepperoni",
                     "Mary": "Cheese",
                     "Helena": "Ham"}
    #return {"date": date.today()}
    return favorite_pizza

#-----------------------------------------------------------------------------------------------------------

@app.route("/posts", methods=["GET"])
def posts():
    # Grab all the posts
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html",
                           posts=posts)

#-----------------------------------------------------------------------------------------------------------
#filters:
# safe
# capitalize
# lower
# upper
# title
# trim
# striptags

#-----------------------------------------------------------------------------------------------------------

# Create a route decorator
@app.route("/")
def index():
    first_name = "Naraeha"
    stuff = "This is bold text"
    favorite_pizza = ["Pepperoni", "cheese", "mushrooms", 41]
    return render_template("index.html", 
                           template_first_name=first_name,
                           template_stuff=stuff,
                           template_pizza=favorite_pizza)

#-----------------------------------------------------------------------------------------------------------

# Create Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesfull.")
                return redirect(url_for("dashboard"))
            else:
                flash("Wrong Password")
        else:
            flash("Username Not Found.")
    return render_template("login.html", form=form)

#-----------------------------------------------------------------------------------------------------------
# Create logout page
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("login"))

#-----------------------------------------------------------------------------------------------------------

# Create name page
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    # validate
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form submitted Successfully")
    return render_template("name.html",
                           name=name,
                           form=form)

#-----------------------------------------------------------------------------------------------------------

@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

#-----------------------------------------------------------------------------------------------------------

#Pass stuff to nav bar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # get data from submited form
        post.searched = form.searched.data
        # Query the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()

        return render_template("search.html", form=form, searched=post.searched, posts=posts)


#-----------------------------------------------------------------------------------------------------------

# Create password test page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # validate
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form
        form.email.data = ""
        form.password_hash.data = ""

        # Lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
        
    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)

#-----------------------------------------------------------------------------------------------------------

# update database
@app.route("/update/<int:id>", methods=["POST", "GET"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.usernamme = request.form["username"]
        try:
            db.session.commit()
            flash("User updated Successfully.")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Error - Something went wrong in updating the database.")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
         return render_template("update.html", form=form, name_to_update=name_to_update, id=id)

#-----------------------------------------------------------------------------------------------------------

# localhost:5000/user/naraeha
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", template_name=name)

#-----------------------------------------------------------------------------------------------------------

# create custom error pages

# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# iternal server error pages
@app.errorhandler(500)
def page_not_found(e):
    return render_template("50.html"), 500



#------------------------------------------------------------------------------------------------------------#                         
#------------------------------------DATABASE MODELS --------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------#

# Create database model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(200), nullable=True)

    # Password
    password_hash = db.Column(db.String(128))
    # User can have many posts
    posts = db.relationship("Posts", backref="poster")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #Create a string
    def __repr__(self):
        return "<Name %r>" % self.name

#-----------------------------------------------------------------------------------------------------------

# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text())
    #author = db.Column(db.String(200), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(200))
    # foreign key to link Users (refer to the primary key of the user)
    poster_id =db.Column(db.Integer, db.ForeignKey("users.id"))

#-----------------------------------------------------------------------------------------------------------