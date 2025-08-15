from flask import Blueprint, g, jsonify, request

from server.exceptions import ConversionError, DatabaseError, RecordNotFoundError
from server.model.service.admin.admin_service import AdminService
from server.model.tables import AccountType, User
from server.route.requires_auth_wrapper import requires_auth

admin = Blueprint('admin', __name__, url_prefix="/admin")

@admin.route("/new-librarian", methods=["POST"])
@requires_auth(AccountType.ADMIN)
def new_librarian():
    pass

@admin.route("/users", methods=["GET"])
@requires_auth(AccountType.ADMIN)
def get_users():
    users = AdminService(g.Session).get_users()

    data = []
    for user in users:
        data.append(user.to_dict())

    for d in data:
        del d["password"]

    return jsonify({
        "message": "Users retreived",
        "data": data
    }), 200

@admin.route("/suspend-user", methods=["POST"])
@requires_auth(AccountType.ADMIN)
def suspend_user():
    data = request.json
    user_id = data.get("id")

    if user_id is None:
        return jsonify({"error": f"Missing id field"}), 400

    try:
        user_id = User.str_to_int(user_id)
    except ConversionError as e:
        return jsonify({"error": f"Invalid id {user_id}"}), 400

    try:
        user = AdminService(g.Session).get_users(id=user_id)
    except RecordNotFoundError:
        return jsonify({"error": f"User id {user_id} not found"}), 404

    AdminService(g.Session).suspend_user(user)

    return jsonify({"message": f"User suspended succesfully"}), 200

@admin.route("/reinstate-user", methods=["POST"])
@requires_auth(AccountType.ADMIN)
def reinstate_user():
    data = request.json
    user_id = data.get("id")

    if user_id is None:
        return jsonify({"error": f"Missing id field"})

    try:
        user_id = User.str_to_int(user_id)
    except ConversionError as e:
        return jsonify({"error": f"Invalid id {user_id}"}), 400

    try:
        user = AdminService(g.Session).get_users(id=user_id)
    except RecordNotFoundError:
        return jsonify({"error": f"User id {user_id} not found"}), 404
    
    AdminService(g.Session).reinstate_user(user)

    return jsonify({"message": f"User reinstated succesfully"}), 200