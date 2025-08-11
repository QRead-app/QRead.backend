from flask import Blueprint, g, jsonify, request

from server.exceptions import ConversionError, DatabaseError
from server.model.service.admin.admin_service import AdminService
from server.model.tables import AccountType, User
from server.route.requires_auth_wrapper import requires_auth

admin = Blueprint('admin', __name__, url_prefix="/admin")

@admin.route("/new-librarian", methods=["POST"])
@requires_auth(AccountType.ADMIN)
def new_librarian():
    pass

@admin.route("/get-users", methods=["GET"])
@requires_auth(AccountType.ADMIN)
def get_users():
    try:
        users = AdminService(g.Session).get_users()
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    return users

@admin.route("/suspend-user", methods=["POST"])
@requires_auth(AccountType.ADMIN)
def suspend_user():
    data = request.json
    user_id = data.get("id")

    try:
        user_id = User.str_to_int(user_id)
    except ConversionError as e:
        return jsonify({"error": str(e)}), 400

    try:
        user = AdminService(g.Session).get_users(id=user_id)
        AdminService(g.Session).suspend_user(user)
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    return user

@admin.route("/reinstate-user", methods=["POST"])
@requires_auth(AccountType.ADMIN)
def reinstate_user():
    data = request.json
    user_id = data.get("id")

    try:
        user_id = User.str_to_int(user_id)
    except ConversionError as e:
        return jsonify({"error": str(e)}), 400

    try:
        user = AdminService(g.Session).get_users(id=user_id)
        AdminService(g.Session).reinstate_user(user)
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    return user