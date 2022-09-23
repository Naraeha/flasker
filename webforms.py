from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

# Create login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Post Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    about_author = TextAreaField("About Author")
    password_hash = PasswordField("password", validators=[DataRequired(), EqualTo("password_hash2", message="passwords Must Match.")])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    profile_pic = FileField("profile pic")
    submit = SubmitField("Submit")

# Create a form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a password Form Class
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Search Form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
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