from flask import Blueprint, g, request, session, jsonify
from server.exceptions import ConversionError, DatabaseError, IncorrectCredentialsError, RecordNotFoundError
from server.model.service.common_service import CommonService
from server.model.tables import AccountType, Book, User

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

    if email is None:
        return jsonify({"error": "Missing email field"}), 400
    if password is None:
        return jsonify({"error": "Missing password field"}), 400

    if not User.is_email(email):
        return jsonify({"error": f"Invalid email {email}"}), 400

    try:
        user = CommonService(g.Session).authenticate(email, password, account_type)
    except IncorrectCredentialsError:
        return jsonify({"error": "Authentication failed"}), 401

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

    id = data.get("id")
    title = data.get("title")
    description = data.get("description")
    author = data.get("author")
    condition = data.get("condition")

    if id is not None:
        try:
            id = Book.str_to_int(id)
        except ConversionError:
            return jsonify({"error": f"Invalid book id {id}"}), 400
    
    if condition is not None:
        try:
            condition = Book.str_to_book_condition(condition)
        except ConversionError:
            return jsonify({"error": f"Invalid book condition {condition}"}), 400

    try:
        result = CommonService(g.Session).get_book(
            id,
            title,
            description,
            author,
            condition,
        )
    except RecordNotFoundError:
        return jsonify({"message": "No book found"}), 200

    books: list[Book] = []
    for book in result:
        books.append(book.to_dict())

    return jsonify({
        "message": "Book(s) retrieved",
        "data": books
    }), 200