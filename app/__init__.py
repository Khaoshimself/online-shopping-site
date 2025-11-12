from os import environ
from flask import Flask, render_template
from flask_login import LoginManager
from app.routes.user_management import init_user_management
from app.routes.cart_api import cart_api_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = environ.get("SECRET_KEY", "secret")
login = LoginManager(app)

app.register_blueprint(cart_api_bp)
init_user_management(app, login)
