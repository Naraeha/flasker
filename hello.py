from flask import Flask, render_template

# Create a flask instance
app = Flask(__name__)

#filters:
# safe
# capitalize
# lower
# upper
# title
# trim
# striptags


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
