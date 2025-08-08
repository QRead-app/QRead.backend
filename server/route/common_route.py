from flask import Blueprint, g, request, session, jsonify
from server.model.service.common_service import CommonService
from server.model.tables import AccountType

common = Blueprint('common', __name__)

@common.route("/<type>/login", methods=["POST"])
def login(type: str):
    data = request.json
    email = data["email"]
    password = data["password"]

    try:
        account_type = AccountType[type.upper()]
    except KeyError:
        return jsonify({"message": f"Invalid path {type}"}), 404

    auth = CommonService(g.Session).authenticate(email, password, account_type)

    if auth:
        session["session"] = {"email": email, "account_type": account_type.name}
        return jsonify({"message": "Login successful"}), 200
    
    return jsonify({"message": "Authentication failed"}), 401

@common.route("/logout", methods=["POST"])
def logout():
    if "session" in session:
        session.pop("session")
        return jsonify({"message": "Logout successful"}), 200
    
    return jsonify({"message": "No active session"}), 204

