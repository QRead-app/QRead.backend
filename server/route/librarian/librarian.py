from flask import Blueprint, g, jsonify, request, session

from server.exceptions import BookBorrowingError, ConversionError, RecordNotFoundError
from server.model.service.common_service import CommonService
from server.model.service.librarian.librarian_service import LibrarianService
from server.model.tables import AccountType, Book, Fine, User
from server.route.requires_auth_wrapper import requires_auth

librarian = Blueprint('librarian', __name__, url_prefix="/librarian")

@librarian.route("/fine", methods=["POST"])
@requires_auth(AccountType.LIBRARIAN)
def issue_fine():
    data = request.json
    user_id = data.get("user_id")
    transaction_id = data.get("transaction_id")
    amount = data.get("amount")
    reason = data.get("reason")
    
    if user_id is None:
        return jsonify({"error": "Missing user_id field"}), 400
    if transaction_id is None:
        return jsonify({"error": "Missing transaction_id field"}), 400
    if amount is None:
        return jsonify({"error": "Missing amount field"}), 400
    if reason is None:
        return jsonify({"error": "Missing reason field"}), 400

    try:
        user_id = Fine.str_to_int(user_id)
    except ConversionError:
        return jsonify({"error": f"Invalid user_id {user_id}"}), 400
    
    try:
        transaction_id = Fine.str_to_int(transaction_id)
    except ConversionError as e:
        return jsonify({"error": f"Invalid transaction id {transaction_id}"}), 400
        
    try:
        amount = Fine.str_to_decimal(amount)
    except ConversionError as e:
        return jsonify({"error": f"Invalid amount {amount}"}), 400
    
    LibrarianService(g.Session).issue_fine(user_id, transaction_id, amount, reason)
    
    return jsonify({"message": "Fine issued successfully"}), 200

@librarian.route("/book", methods=["POST"])
@requires_auth(AccountType.LIBRARIAN)
def add_book():
    data = request.json
    title = data.get("title")
    description = data.get("description")
    author = data.get("author")
    condition = data.get("condition")
    
    if title is None:
        return jsonify({"error": "Missing title field"}), 400
    if description is None:
        return jsonify({"error": "Missing description field"}), 400
    if author is None:
        return jsonify({"error": "Missing author field"}), 400
    if condition is None:
        return jsonify({"error": "Missing condition field"}), 400
    
    try:
        condition = Book.str_to_book_condition(condition)
    except ConversionError as e:
        return jsonify({"error": f"Invalid condition {condition}"}), 400

    book = LibrarianService(g.Session).add_book(title, description, author, condition)
    
    return jsonify({"message": "Book added successfully", "data": book.to_dict()}), 200

@librarian.route("/books", methods=["GET"])
@requires_auth(AccountType.LIBRARIAN)
def search_books():
    data = request.args
    search = data.get("search")

    try:
        books = LibrarianService(g.Session).search_books(search)
    except RecordNotFoundError:
        return jsonify({"message": "No book found"}), 200
    
    result = []
    for book in books:
        result.append(book.to_dict())

    return jsonify({
        "message": "Book search success",
        "data": data   
    }), 200

@librarian.route("/book", methods=["DELETE"])
@requires_auth(AccountType.LIBRARIAN)
def remove_book():
    data = request.args
    book_id = data.get("book_id")

    if book_id is None:
        return jsonify({"error": "Missing book_id field"}), 400

    try:
        book_id = Book.str_to_int(book_id)
    except ConversionError as e:
        return jsonify({"error": "Invalid book_id {book_id}"}), 400 

    try:
        data = LibrarianService(g.Session).remove_book(book_id)
    except RecordNotFoundError:
        return jsonify({"error": f"Book id {book_id} not found"}), 404
    
    return jsonify({"message": "Book removed successfully"}), 200

@librarian.route("/book", methods=["PUT"])
@requires_auth(AccountType.LIBRARIAN)
def update_book():
    data = request.json
    book_id = data.get("id")
    book_title = data.get("title")
    book_description = data.get("description")
    book_author = data.get("author")
    book_condition = data.get("condition")
    book_on_loan = data.get("on_loan")

    if book_id is None:
        return jsonify({"error": "Missing id field"}), 400
    try:
        book_id = Book.str_to_int(book_id)
    except ConversionError:
        return jsonify({"error": f"Invalid id {book_id}"})

    if book_condition:
        try:
            book_condition = Book.str_to_book_condition(book_condition)
        except ConversionError as e:
            return jsonify({"error": f"Invalid condition {book_condition}"}), 400 

    new_book = Book(
        id = book_id,
        title = book_title,
        description = book_description,
        author = book_author,
        condition = book_condition,
        on_loan = book_on_loan
    )

    try:
        LibrarianService(g.Session).update_book(book_id, new_book)
    except RecordNotFoundError:
        return jsonify({"error": f"Book {book_id} does not exist"}), 404 

    return jsonify({"message": "Book updated successfully"}), 200

@librarian.route("/return-book", methods=["POST"])
@requires_auth(AccountType.LIBRARIAN)
def return_book():
    data = request.json
    book_id = data.get("id")

    if book_id is None:
        return jsonify({"error": "Missing id field"}), 400

    try:
        book_id = Book.str_to_int(book_id)
    except ConversionError:
        return jsonify({"error": f"Invalid id {book_id}"}), 400
    
    try:
        LibrarianService(g.Session).return_book(
            session["session"]["id"],
            book_id
        )
    except RecordNotFoundError:
        return jsonify({"error": f"Book id {book_id} not found"}), 404
    except BookBorrowingError:
        return jsonify({"error": f"Book id {book_id} is not borrowed"}), 400
    
    return jsonify({"message": "Book returned successfully"}), 200

@librarian.route("/account", methods=["PUT"])
@requires_auth(AccountType.LIBRARIAN)
def update_account():
    data = request.json
    id = data.get("id") 
    name = data.get("name") 
    email = data.get("email") 
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

    try:
        LibrarianService(g.Session).update_user(
            id = id,
            name = name,
            email = email,
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