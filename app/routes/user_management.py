from urllib.parse import urlsplit

from bson import ObjectId
from flask import render_template, redirect, url_for, Flask, flash, request
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from app.records.users import db_user_verify_login, User, db_user_create
from app.database import db

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

def init_user_management(app: Flask, login_manager : LoginManager):

    login_manager.login_view = '/login'
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect('/index')
        form = LoginForm()
        if form.validate_on_submit():
            user = db_user_verify_login(form.username.data, form.password.data)
            if user is None:
                flash('Invalid username or password')
                return redirect('/login')
            login_user(user,remember=False)
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                return redirect('/index')
            return redirect(next_page)
        return render_template('auth/login.html',title='Sign In', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect('/index')

    @app.route('/usersettings',methods=['GET','POST'])
    @login_required
    def user_settings():
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if not current_user.check_password(form.current_password.data):
                flash('Wrong password')
                return redirect('/usersettings')
            need_logout = False
            if form.new_password.data is not None and form.new_password.data != '':
                if form.verify_password.data != form.new_password.data:
                    flash('passwords do not match')
                    return redirect('/usersettings')
                current_user.update_password(form.new_password.data)
                need_logout = True
            if form.username.data is not None and form.username.data != '':
                current_user.update_username(form.username.data)
                need_logout = True

            if need_logout:
                logout_user()
                return redirect('/login')

        return render_template('auth/updateuser.html',title='Update User', form=form)

    @app.route('/deleteuser',methods=['GET','POST'])
    @login_required
    def delete_user():
        form = DeleteAccountForm()
        if form.validate_on_submit():
            if current_user.check_password(form.current_password.data):
                current_user.delete_user()
                logout_user()
                flash('You have been deleted')
                return redirect('/index')
        return render_template('auth/deleteuser.html',title='Delete User', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect('/index')
        form = RegisterForm()
        if form.validate_on_submit():
            if form.verify_password.data != form.password.data:
                flash('passwords do not match')
                return redirect('/signup')
            db_user_create(form.username.data, form.password.data)
            return redirect('/login')
        return render_template('auth/signup.html',title='Sign Up', form=form)


    @login_manager.user_loader
    def load_user(user_id):
        model = db.users.find_one({"_id": ObjectId(user_id)})
        if model is None:
            return None
        return User(model)

    @login_manager.request_loader
    def load_user_from_request(request) -> User | None:
        auth_token = request.args.get("auth_token")
        if auth_token:
            user = db.users.find_one({"auth_token": auth_token})
            if user:
                return User(user)

        auth_token = request.headers.get('Authorization')
        if auth_token:
            auth_token.replace('Bearer ', '')
            auth_token = auth_token.replace('Bearer ', '')
            user = db.users.find_one({"auth_token": auth_token})
            if user:
                return User(user)
        return None

