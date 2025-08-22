from flask import Blueprint, g, request, session, jsonify
from server.exceptions import AuthorizationError, ConversionError, EmailAlreadyExistsError, IncorrectCredentialsError, RecordNotFoundError
from server.model.service.admin.admin_service import AdminService
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
    except AuthorizationError:
        return jsonify({"error": "User is suspended"}), 400
    
    session["authenticate"] = {"id": user.id, "account_type": account_type.name}

    return jsonify({
        "message": "Authenticated"
    }), 200

@common.route("/verify-otp", methods = ["POST"])
def verify_otp():
    data = request.json
    sess = session.get("authenticate")

    if sess is None:
        return jsonify({"error": "Not authenticated"}), 401

    user_id = sess.get("id")
    onetimepass = data.get("otp")

    if user_id is None:
        return jsonify({"error": "Not authenticated"}), 401
    
    if onetimepass is None:
        return jsonify({"error": "Missing otp field"}), 400

    try:
        verification = CommonService(g.Session).verify_otp(user_id, onetimepass)
    except RecordNotFoundError:
        return jsonify({"error": "Not authenticated"}), 401
    
    if not verification:
        return jsonify({"error": "Wrong OTP"}), 401 
    
    session["session"] = session["authenticate"]
    del session["authenticate"]

    return jsonify({"message": "Login successful"}), 200

@common.route("/logout", methods=["POST"])
def logout():
    if "session" in session:
        session.pop("session")
        return jsonify({"message": "Logout successful"}), 200
    
    return jsonify({"message": "No active session"}), 200

@common.route("/book", methods=["GET"])
def get_book():
    data = request.args

    id = data.get("id")
    title = data.get("title")
    description = data.get("description")
    author = data.get("author")
    condition = data.get("condition")
    on_loan = data.get("on_loan")

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
        
    if on_loan is not None:
        if type(on_loan) is not bool:
            return jsonify({"error": f"Invalid on_load {on_loan}"}), 400

    try:
        result = CommonService(g.Session).get_book(
            id,
            title,
            description,
            author,
            condition,
            on_loan
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

@common.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    if email is None:
        return jsonify({"error": "Missing email field"}), 400
    
    if not User.is_email(email):
        return jsonify({"error": f"Invalid email {email}"}), 400
    
    try:
        CommonService(g.Session).forgot_password(email)
    except RecordNotFoundError:
        return jsonify({"error": "Email not found"}), 404
    # except AuthorizationError:
    #     return jsonify({"error": "Admin cannot use this service"}), 401
    
    return jsonify({"message": "Reset password email sent"}), 200

@common.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    secret = data.get("secret")
    password = data.get("password")

    if secret is None:
        return jsonify({"error": "Missing secret field"}), 400
    
    if password is None:
        return jsonify({"error": "Missing password field"}), 400
    
    try:
        CommonService(g.Session).reset_password(secret, password)
    except IncorrectCredentialsError:
        return jsonify({"error": f"Wrong secret {secret}"}), 401
    except RecordNotFoundError:
        return jsonify({"error": "User does not exist"}), 404
    
    return jsonify({"message": "Password successfully updated"}), 200

@common.route("/new-librarian", methods=["POST"])
def new_librarian():
    data = request.json
    secret = data.get("secret")
    name = data.get("name")
    password = data.get("password")

    if secret is None:
        return jsonify({"error": "Missing secret field"}), 400
    
    if name is None:
        return jsonify({"error": "Missing name field"}), 400
    
    if password is None:
        return jsonify({"error": "Missing password field"}), 400
    
    try:
        AdminService(g.Session).new_librarian(secret, name, password)
    except EmailAlreadyExistsError as e:
        return jsonify({"error": f"Email {e} is already registered"}), 400
    except RecordNotFoundError:
        return jsonify({"error": "Not authenticated"}), 401
    except IncorrectCredentialsError:
        return jsonify({"error": f"Wrong secret {secret}"}), 401 


    return jsonify({"message": "Librarian created successfully"}), 200