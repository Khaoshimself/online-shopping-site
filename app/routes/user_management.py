from typing import Optional
from urllib.parse import urlsplit
from bson import ObjectId
from flask import render_template, redirect, url_for, Flask, flash, request, jsonify, session
from flask_login import (
    current_user,
    login_user,
    login_required,
    logout_user,
    LoginManager,
    UserMixin,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from app.records.users import db_user_verify_login, User, db_user_create, get_users


# Forms
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    verify_password = PasswordField("Verify Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username")
    new_password = PasswordField("New Password")
    verify_password = PasswordField("Verify Password", validators=[DataRequired()])
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    submit = SubmitField("Update")


class DeleteAccountForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    submit = SubmitField("Delete")


# Init
def init_user_management(app: Flask, login_manager: LoginManager):

    login_manager.login_view = (
        "login"  # where @login_required redirects when not authed
    )

    # Demo user for quick testing
    class DummyUser(UserMixin):
        id = 1
        username = "test"

        def get_name(self):
            return self.username

        def check_password(self, password):
            return password == "test"

        def update_password(self, password):
            print("DummyUser: Password updated (not really)")
            pass

        def update_username(self, username):
            print("DummyUser: Username updated (not really)")
            pass

        def delete_user(self):
            print("DummyUser: User deleted (not really)")
            pass


    # MONGO STUFF
    from pymongo import MongoClient
    from dotenv import load_dotenv
    import os

    load_dotenv()

    mongo_user = os.getenv("MONGO_ROOT_USER")
    mongo_password = os.getenv("MONGO_ROOT_PASSWORD")

    client = MongoClient(
        f"mongodb://{mongo_user}:{mongo_password}@mongo:27017/?authSource=admin"
    )
    db = client["shop"]
    products_col = db["products"]
    orders_col = db["orders"]

    @app.route("/")
    @app.route("/index")
    def catalog():
        """Main product catalog/shop page with search + sorting."""
        q = request.args.get("q", "").strip()
        sort = request.args.get("sort", "name")  

    # Serch query
        mongo_query = {}
        if q:
            mongo_query = {
                "$or": [
                    {"name": {"$regex": q, "$options": "i"}},
                    {"description": {"$regex": q, "$options": "i"}},
                ]
            }

    # Determining the sorting order
        if sort == "price_asc":
            sort_field = "price"
            sort_dir = 1       # low → high

        elif sort == "price_desc":
            sort_field = "price"
            sort_dir = -1      # high → low

        elif sort == "availability":
            sort_field = "quantity"
            sort_dir = -1      # most available first

        else:
            sort_field = "name"
            sort_dir = 1       # A → Z         

        cursor = products_col.find(mongo_query).sort(sort_field, sort_dir)
        products = list(cursor)

        return render_template(
            "shop/index.html",
            title="Shop",
            products=products,
            q=q,
            sort=sort,  
        )

    @app.route("/cart")
    def cart():
        """Renders the main cart page template."""
        # The template itself is just a shell.
        return render_template("cart/cart.html", title="Your Cart")    

    # This route name "home" conflicts with "/", so we'll point it to login
    @app.route("/home", methods=["GET"])
    def home():
        # Always show the login page on /
        return redirect(url_for("login"))

    # /login stays as the canonical login handler
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("catalog"))

        form = LoginForm()
        if form.validate_on_submit():
            # if form.username.data is None or form.password.data is None:
            #    flash("Invalid username or password", "danger")
            #    return redirect(url_for("login"))
            if form.username.data == "test" and form.password.data == "test":
                user = DummyUser()
            else: 
                user = db_user_verify_login(form.username.data, form.password.data)
            if user is not None:
                login_user(user, remember=False)
                
                # --- THIS IS THE NEW JSON "BRIDGE" ---
                # Check if the request is from our auth.js script
                if request.is_json:
                    # Clear session cart if it exists (new login)
                    session.pop("cart", None) 
                    return jsonify({
                        "message": "Login successful! Redirecting...",
                        "redirect": url_for("catalog") # Tell JS to go to the shop
                    }), 200
                # --- END OF BRIDGE ---
                
                flash("Welcome back!", "success")

                next_url = request.args.get("next")
                if next_url and urlsplit(next_url).netloc == "":
                    return redirect(next_url)
                return redirect(url_for("catalog")) # Go to shop page

            # --- THIS IS THE NEW JSON "BRIDGE" FOR ERRORS ---
            if request.is_json:
                return jsonify({
                    "message": "Invalid username or password."
                }), 401 # 401 Unauthorized
            # --- END OF BRIDGE ---

            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

        return render_template("auth/login.html", title="Login", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        session.pop("cart", None)
        flash("You have been logged out.")
        return redirect(url_for("login"))

    @app.route("/usersettings", methods=["GET", "POST"])
    @login_required
    def user_settings():
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if not current_user.check_password(form.current_password.data):
                flash("Wrong password")
                return redirect(url_for("user_settings"))

            need_logout = False

            if form.new_password.data:
                if form.verify_password.data != form.new_password.data:
                    flash("Passwords do not match")
                    return redirect(url_for("user_settings"))
                current_user.update_password(form.new_password.data)
                need_logout = True

            if form.username.data:
                current_user.update_username(form.username.data)
                need_logout = True

            if need_logout:
                logout_user()
                return redirect(url_for("login"))

            flash("Account updated.") # Added a success flash message

        return render_template("auth/updateuser.html", title="Update User", form=form)

    @app.route("/deleteuser", methods=["GET", "POST"])
    @login_required
    def delete_user():
        form = DeleteAccountForm()
        if form.validate_on_submit():
            if current_user.check_password(form.current_password.data):
                current_user.delete_user()
                logout_user()
                flash("You have been deleted")
                return redirect(url_for("login"))
            else:
                flash("Incorrect password. Account not deleted.")
        return render_template("auth/deleteuser.html", title="Delete User", form=form)

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("catalog")) # Go to shop page

        form = RegisterForm()
        if form.validate_on_submit():
            if form.username.data is None or form.password.data is None:
                # --- JSON BRIDGE FOR ERRORS ---
                if request.is_json:
                    return jsonify({"message": "Invalid username or password"}), 400
                flash("Invalid username or password", "danger")
                return redirect(url_for("signup"))
                
            if form.verify_password.data != form.password.data:
                # --- JSON BRIDGE FOR ERRORS ---
                if request.is_json:
                    return jsonify({"message": "Passwords do not match."}), 400
                flash("Passwords do not match")
                return redirect(url_for("signup"))

            # --- Add error handling for existing user ---
            try:
                # This function does not check if user exists, so we wrap it
                db_user_create(form.username.data, form.password.data)
            except Exception as e:
                # This will catch if the user already exists (or other DB errors)
                # --- JSON BRIDGE FOR ERRORS ---
                if request.is_json:
                    return jsonify({"message": "Username already taken."}), 400
                flash("Username already taken.")
                return redirect(url_for("signup"))

            # --- JSON BRIDGE FOR SUCCESS ---
            if request.is_json:
                return jsonify({
                    "message": "Account created! Please log in.",
                    "redirect": url_for("login")
                }), 201 # 201 Created

            flash("Account created. Please log in.")
            return redirect(url_for("login"))

        return render_template("auth/signup.html", title="Sign Up", form=form)

    # Flask-Login optional persistent user sessions
    @login_manager.user_loader
    def load_user(user_id):
        # Check if DummyUser
        if user_id == "1":
            return DummyUser()

        try: 
            model = db.users.find_one({"_id": ObjectId(user_id)})
            if model is None:
                return None
            return User(model)
        except:
            None

    @login_manager.request_loader
    def load_user_from_request(req) -> Optional[User]:
        u = get_users()
        if u is None:
            return None
        # Query param token
        auth_token = req.args.get("auth_token")
        if auth_token:
            user = u.find_one({"auth_token": auth_token})
            if user:
                return User(user)

        # Bearer header token
        auth_header = req.headers.get("Authorization")
        if auth_header:
            token = auth_header.replace("Bearer ", "").strip()
            user = u.find_one({"auth_token": token})
            if user:
                return User(user)

        return None

    @app.route("/orders/<order_id>")
    def order_confirmation(order_id):
        try:
            obj_id = ObjectId(order_id)
        except Exception:
            abort(404)

        order = orders_col.find_one({"_id": obj_id})
        if not order:
            abort(404)

        return render_template("order_confirmation.html", order=order, order_id=order_id)
