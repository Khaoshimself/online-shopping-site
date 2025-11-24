from bson import ObjectId
from flask import Blueprint, redirect, request, jsonify, render_template, url_for
import app.database
from app.database import create_item, init_db
from app.records.users import User, UserType, find_user, get_users
from flask_login import current_user, login_required, login_user

from typing import Optional

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired


user_bp = Blueprint("users", __name__, url_prefix="/admin/users")


class EditUserForm(FlaskForm):
    username = StringField("Username")
    new_password = PasswordField("New Password")
    permissions = RadioField(
        "type", choices=[("user", "Normal User"), ("admin", "Admin")]
    )
    submit = SubmitField("Update")


@user_bp.route("/delete", methods=["POST"])
@login_required
def del_user():
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500

    if not (
        isinstance(current_user, User)
        and current_user.get_permissions() == UserType.ADMIN
    ):
        return jsonify({"message": "Access denied"}), 403
    user_id = request.form.get("user_id")
    try:
        user = find_user(ObjectId(user_id))
        if user is None:
            return jsonify({"message": "User doesn't exist"}), 500
        user.delete_user()
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": "Error " + str(e)}), 500


@user_bp.route("/edit/<user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500

    if not (
        isinstance(current_user, User)
        and current_user.get_permissions() == UserType.ADMIN
    ):
        return jsonify({"message": "Access denied"}), 403

    try:
        obj_id = ObjectId(user_id)
    except:
        return jsonify({"message": "Bad Format"}), 500

    try:
        target_result: Optional[User] = find_user(obj_id)
        if target_result is None:
            return jsonify({"error": f"User {user_id} doesn't exist"})
        form = EditUserForm()
        if form.validate_on_submit():
            if form.username.data != target_result.get_name() and isinstance(
                form.username.data, str
            ):
                target_result.update_username(form.username.data)

            if form.new_password.data:
                target_result.update_password(form.new_password.data)

            if form.permissions.data != target_result.get_permissions():
                target_result.update_permissions(form.permissions.data)

            return redirect(url_for("admin_users_page"))
        form.username.data = target_result.get_name()
        form.permissions.data = target_result.get_permissions()

        return render_template(
            "admin/edit-user.html",
            title="Admin - Edit User",
            form=form,
            target=target_result,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route("/", methods=["GET"])
@login_required
def admin_users_page():
    # ensure DB is ready (optional)
    if not app.database.init_db():
        return "Internal error", 500
    # check admin
    if not (
        isinstance(current_user, User)
        and current_user.get_permissions() == UserType.ADMIN
    ):
        return "Access denied", 403

    page = request.args.get("page", 0, type=int)
    u = get_users()
    if u is None:
        return "Internal Error", 500

    total_users = u.count_documents({})
    on_page = u.aggregate([{"$skip": page * 25}, {"$limit": 25}])
    total_pages = (total_users + 24) // 25

    return render_template(
        "admin/users.html",
        title="Admin — Users",
        users=on_page,
        page=page,
        total_pages=total_pages,
    )
