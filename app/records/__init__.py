from flask import Flask, redirect, url_for
from flask_login import LoginManager, UserMixin, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#NOT IN USE RN
class DummyUser(UserMixin):
    def __init__(self):
        self.id = "1"
        self.username = "test"

@login_manager.user_loader
def load_user(user_id):
    # Only ever return the dummy user; no DB calls.
    return DummyUser() if user_id == "1" else None

# make "/" go to index
@app.route("/")
def root():
    return redirect(url_for('index'))
