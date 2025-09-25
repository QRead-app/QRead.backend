from flask import Blueprint, g, jsonify, request, session

from server.exceptions import ConversionError, DatabaseError, EmailAlreadyExistsError, RecordNotFoundError
from server.model.service.admin.admin_service import AdminService
from server.model.tables import AccountType, BookTransaction, Fine, User
from server.route.requires_auth_wrapper import requires_auth

admin = Blueprint('admin', __name__, url_prefix="/admin")

@admin.route("/register-librarian", methods=["POST"])
@requires_auth(AccountType.ADMIN)
def register_librarian():
    data = request.json
    email = data.get("email")
    redirect = data.get("redirect")

    if email is None:
        return jsonify({"error": "Missing email field"}), 400
    if redirect is None:
        return jsonify({"error": "Missing redirect field"}), 400

    if not User.is_email(email):
        return jsonify({"error": f"Invalid email {email}"}), 400
    
    try:
        AdminService(g.Session).register_librarian(email, redirect)
    except EmailAlreadyExistsError as e:
        return jsonify({"error": f"Email {email} is already registered"}), 400

    return jsonify({"message": "Invitation email sent"}), 200

@admin.route("/users", methods=["GET"])
@requires_auth(AccountType.ADMIN)
def get_users():
    data = request.args
    id = data.get("id") 
    name = data.get("name") 
    email = data.get("email") 
    account_type = data.get("type") 
    account_state = data.get("state")

    if id is not None:
        try:
            id = User.str_to_int(id)
        except ConversionError:
            return jsonify({"error": f"Invalid id {id}"}), 400
        
    if email is not None:
        try:
            email = User.is_email(email)
        except ConversionError:
            return jsonify({"error": f"Invalid email {email}"}), 400
        
    if account_type is not None:
        try:
            account_type = User.str_to_account_type(account_type)
        except ConversionError:
            return jsonify({"error": f"Invalid account_type {account_type}"}), 400
        
    if account_state is not None:
        try:
            account_state = User.str_to_account_state(account_state)
        except ConversionError:
            return jsonify({"error": f"Invalid account_state {account_state}"}), 400

    try:
        result = AdminService(g.Session).get_users(
            id = id,
            name = name,
            email = email,
            account_type = account_type,
            account_state = account_state
        )
    except RecordNotFoundError:
        return jsonify({
            "message": "No users found"
        }), 200

    data = []
    for row in result:
        transactions: list[BookTransaction | None] | None = []
        if row[1] is not None:
            for transaction in row[1]:
                transactions.append(
                    transaction.to_dict() if transaction is not None else None)
        else:
            transactions = None

        fines: list[Fine | None] | None = []
        if row[2] is not None:
            for fine in row[2]:
                fines.append(
                    fine.to_dict() if fine is not None else None)
        else:
            fines = None

        users = row[0].to_dict()
        del users["password"]

        data.append({
            "user": users,
            "transaction": transactions,
            "fine": fines
        })

    return jsonify({
        "message": "Users retreived",
        "data": data
    }), 200

@admin.route("/user", methods=["PUT"])
@requires_auth(AccountType.ADMIN)
def update_account():
    data = request.args
    id = data.get("id") 
    name = data.get("name") 
    email = data.get("email") 
    account_type = data.get("type") 
    account_state = data.get("state")
    password = data.get("password")
    newpassword = data.get("newpassword")

    if id is not None:
        try:
            id = User.str_to_int(id)
        except ConversionError:
            return jsonify({"error": f"Invalid id {id}"}), 400
        
    if id is None:
        id = session["session"]["id"]
        
    if email is not None:
        try:
            email = User.is_email(email)
        except ConversionError:
            return jsonify({"error": f"Invalid email {email}"}), 400
        
    if account_type is not None:
        try:
            account_type = User.str_to_account_type(account_type)
        except ConversionError:
            return jsonify({"error": f"Invalid account_type {account_type}"}), 400
        
    if account_state is not None:
        try:
            account_state = User.str_to_account_state(account_state)
        except ConversionError:
            return jsonify({"error": f"Invalid account_state {account_state}"}), 400

    try:
        AdminService(g.Session).update_user(
            id = id,
            name = name,
            email = email,
            account_type = account_type,
            account_state = account_state,
            password = password,
            newpassword = newpassword
        )
    except RecordNotFoundError:
        return jsonify({
            "message": "User not found"
        }), 200

    return jsonify({
        "message": "User updated"
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
        AdminService(g.Session).suspend_user(id=user_id)
    except RecordNotFoundError:
        return jsonify({"error": f"User id {user_id} not found"}), 404

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
        AdminService(g.Session).reinstate_user(id=user_id)
    except RecordNotFoundError:
        return jsonify({"error": f"User id {user_id} not found"}), 404
    
    return jsonify({"message": f"User reinstated succesfully"}), 200

@admin.route("/user", methods=["DELETE"])
@requires_auth(AccountType.ADMIN)
def delete_user():
    data = request.args
    user_id = data.get("id")

    if user_id is None:
        return jsonify({"error": f"Missing id field"})

    try:
        user_id = User.str_to_int(user_id)
    except ConversionError as e:
        return jsonify({"error": f"Invalid id {user_id}"}), 400

    try:
        AdminService(g.Session).delete_user(id=user_id)
    except RecordNotFoundError:
        return jsonify({"error": f"User id {user_id} not found"}), 404
    
    return jsonify({"message": f"User deleted succesfully"}), 200

@admin.route("/app-setting", methods=["PUT"])
@requires_auth(AccountType.ADMIN)
def update_app_setting():
    data = request.json
    key = data.get("key")
    value = data.get("value")

    if key is None:
        return jsonify({"error": f"Missing key field"}), 400
    
    if value is None:
        return jsonify({"error": f"Missing value field"}), 400

    try:
        user = AdminService(g.Session).update_setting(key, value)
    except RecordNotFoundError:
        return jsonify({"error": f"Key {key} not found"}), 404

    return jsonify({"message": f"Setting updated succesfully"}), 200