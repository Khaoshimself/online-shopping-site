from urllib.parse import urlsplit
from bson import ObjectId
from flask import render_template, redirect, url_for, Flask, flash, request
from flask_login import (
    current_user, login_user, login_required, logout_user,
    LoginManager, UserMixin
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from app.records.users import db_user_verify_login, User, db_user_create
from app.database import db


# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    verify_password = PasswordField('Verify Password', validators=[DataRequired()])
    submit = SubmitField('Register')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username')
    new_password = PasswordField('New Password')
    verify_password = PasswordField('Verify Password', validators=[DataRequired()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    submit = SubmitField('Update')


class DeleteAccountForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    submit = SubmitField('Delete')


# Init
def init_user_management(app: Flask, login_manager: LoginManager):

    login_manager.login_view = 'login'  # where @login_required redirects when not authed

    # Demo user for quick testing
    class DummyUser(UserMixin):
        id = 1
        username = "test"

    # Auth Routes
    @app.route('/', methods=['GET'])
    def home():
        # Always show the login page on /
        return render_template('auth/login.html', title='Login', form=LoginForm())

    # /login stays as the canonical login handler
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        form = LoginForm()
        if form.validate_on_submit():
            # TODO: replace with real verification
            if form.username.data == "test" and form.password.data == "123":
                login_user(DummyUser(), remember=False)
                flash('Welcome back!', 'success')

                next_url = request.args.get('next')
                if next_url and urlsplit(next_url).netloc == '':
                    return redirect(next_url)
                return redirect(url_for('dashboard'))

            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        return render_template('auth/login.html', title='Login', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # Main App Pages
    @app.route('/index', endpoint='dashboard')
    @login_required
    def dashboard():
        """Main page (formerly 'index')."""
        return render_template('index.html')

    @app.route('/cart')
    #@login_required
    def cart():
        return render_template('cart/cart.html')

    @app.route('/usersettings', methods=['GET', 'POST'])
    @login_required
    def user_settings():
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if not current_user.check_password(form.current_password.data):
                flash('Wrong password')
                return redirect(url_for('user_settings'))

            need_logout = False

            if form.new_password.data:
                if form.verify_password.data != form.new_password.data:
                    flash('Passwords do not match')
                    return redirect(url_for('user_settings'))
                current_user.update_password(form.new_password.data)
                need_logout = True

            if form.username.data:
                current_user.update_username(form.username.data)
                need_logout = True

            if need_logout:
                logout_user()
                return redirect(url_for('login'))

        return render_template('auth/updateuser.html', title='Update User', form=form)

    @app.route('/deleteuser', methods=['GET', 'POST'])
    @login_required
    def delete_user():
        form = DeleteAccountForm()
        if form.validate_on_submit():
            if current_user.check_password(form.current_password.data):
                current_user.delete_user()
                logout_user()
                flash('You have been deleted')
                return redirect(url_for('login'))
        return render_template('auth/deleteuser.html', title='Delete User', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        form = RegisterForm()
        if form.validate_on_submit():
            if form.verify_password.data != form.password.data:
                flash('Passwords do not match')
                return redirect(url_for('signup'))

            db_user_create(form.username.data, form.password.data)
            flash('Account created. Please log in.')
            return redirect(url_for('login'))

        return render_template('auth/signup.html', title='Sign Up', form=form)

    # Flask-Login optional persistent user sessions
    """
    @login_manager.user_loader
    def load_user(user_id):
        model = db.users.find_one({"_id": ObjectId(user_id)})
        if model is None:
            return None
        return User(model)
    """

    @login_manager.request_loader
    def load_user_from_request(req) -> User | None:
        # Query param token
        auth_token = req.args.get("auth_token")
        if auth_token:
            user = db.users.find_one({"auth_token": auth_token})
            if user:
                return User(user)

        # Bearer header token
        auth_header = req.headers.get('Authorization')
        if auth_header:
            token = auth_header.replace('Bearer ', '').strip()
            user = db.users.find_one({"auth_token": token})
            if user:
                return User(user)

        return None
