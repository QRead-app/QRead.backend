from flask import Blueprint, g, request, session, jsonify
from server.exceptions import DatabaseError, IncorrectCredentialsError
from server.model.service.common_service import CommonService
from server.model.tables import AccountType, User

common = Blueprint('common', __name__)

@common.route("/<type>/login", methods=["POST"])
def login(type: str):
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        account_type = AccountType[type.upper()]
    except KeyError:
        return jsonify({"error": f"Invalid path {type}"}), 404

    if (
        email is None
        or password is None
    ):
        return jsonify({"error": "Missing fields"}), 400
        
    common_service = CommonService(g.Session)

    try:
        user = common_service.authenticate(email, password, account_type)
    except IncorrectCredentialsError as e:
        return jsonify({"error": str(e)}), 401
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    session["session"] = {"id": user.id, "account_type": account_type.name}
    return jsonify({"message": "Login successful"}), 200

@common.route("/logout", methods=["POST"])
def logout():
    if "session" in session:
        session.pop("session")
        return jsonify({"message": "Logout successful"}), 200
    
    return jsonify({"message": "No active session"}), 200

@common.route("/get-book", methods=["GET"])
def get_book():
    data = request.json
    book = data.get("book")

    try:
        result = CommonService(g.Session).get_book(
            book.get("id", None),
            book.get("title", None),
            book.get("description", None),
            book.get("author", None),
            book.get("condition", None),
        )
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    if len(result) == 0:
        return jsonify({"error": "Book not found"}), 404
    
    return result