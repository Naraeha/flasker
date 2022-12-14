from sqlite3 import DataError, DatabaseError
from xml.sax.handler import property_declaration_handler
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# Create a flask instance
app = Flask(__name__)
# Add database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# sql
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# mysql://username:password@localhost/db_name
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:freeto753@localhost/our_users'

# Secret key
app.config["SECRET_KEY"] = "secret key"
#Initialize The database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)

# Create Json
@app.route("/date")
def get_current_date():
    favorite_pizza= {"Naraeha": "Pepperoni",
                     "Mary": "Cheese",
                     "Helena": "Ham"}
    #return {"date": date.today()}
    return favorite_pizza

# Flask Login system
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

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

# Create logout page
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("login"))

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
        try:
            db.session.commit()
            flash("User updated Successfully.")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error - Something went wrong in updating the database.")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
    else:
         return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
    

#Create database model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Password
    password_hash = db.Column(db.String(128))

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

# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    author = db.Column(db.String(200), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(200))

# Create a Post Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Add Post Page
@app.route("/add-post", methods=["GET", "POST"])
#@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     author=form.author.data,
                     slug=form.slug.data)
        # Clear the form
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""

        # Add post to the database
        db.session.add(post)
        db.session.commit()
        
        # Return a message
        flash("Blog Post Submitted Successfully.")

    # redirect to the webpage
    return render_template("add_post.html", form=form)

@app.route("/posts", methods=["GET"])
def posts():
    # Grab all the posts
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html",
                           posts=posts)

#filters:
# safe
# capitalize
# lower
# upper
# title
# trim
# striptags

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

# localhost:5000/user/naraeha
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", template_name=name)


# create custom error pages

# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# iternal server error pages
@app.errorhandler(500)
def page_not_found(e):
    return render_template("50.html"), 500


# Create a form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField("password", validators=[DataRequired(), EqualTo("password_hash2", message="passwords Must Match.")])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Submit")

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



# update database
@app.route("/update/<int:id>", methods=["POST", "GET"])
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

        

# Create a form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a password Form Class
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")

    #BooleanField
    #DateField
    #DateTimeField
    #DecimalField
    #FileField
    #HiddenField
    #MultipleField
    #FieldList
    #FloatField
    #FormField
    #IntegerField
    #PasswordField
    #RadioField
    #SelectField
    #SelectMultipleField
    #SubmitField
    #StringField
    #TextAreaField
    
    ##Validators
    #DataRequired
    #Email
    #EqualTo
    #InputRequired
    #IPAdress
    #Lenght
    #MacAddress
    #NumberRange
    #Optional
    #Regexp
    #URL
    #UUID
    #AnyOf
    #NoneOf
    
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

@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        db.session.add(post)
        db.session.commit()
        flash("Post has been updated.")
        return redirect(url_for("post", id=post.id))
    
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("edit.html", form=form)
    
@app.route("/posts/delete/<int:id>")
def delete_post(id):
    post_delete = Posts.query.get_or_404(id)
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