from os import environ

from flask import Flask, render_template
from flask_login import LoginManager
from app.routes.user_management import init_user_management

app = Flask(__name__)
app.config['SECRET_KEY'] = environ.get('SECRET_KEY',"secret")
login = LoginManager(app)

@app.route("/")
@app.route("/index")
def catalog():
    return render_template("shop/index.html")

init_user_management(app,login)
