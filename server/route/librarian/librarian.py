from flask import Blueprint, g, jsonify, request

from server.exceptions import ConversionError, DatabaseError
from server.model.service.common_service import CommonService
from server.model.service.librarian.librarian_service import LibrarianService
from server.model.tables import AccountType, Book, Fine
from server.route.requires_auth_wrapper import requires_auth

librarian = Blueprint('librarian', __name__, url_prefix="/librarian")

@librarian.route("/issue-fine", methods=["POST"])
@requires_auth(AccountType.LIBRARIAN)
def issue_fine():
    data = request.json
    user_id = data.get("user_id")
    transaction_id = data.get("transaction_id")
    amount = data.get("amount")
    reason = data.get("reason")
    
    if user_id is None:
        return jsonify({"error": "Missing user_id field"}), 400
    if amount is None:
        return jsonify({"error": "Missing amount field"}), 400
    if reason is None:
        return jsonify({"error": "Missing reason field"}), 400

    try:
        user_id = Fine.str_to_int(user_id)
        transaction_id = Fine.str_to_int(transaction_id)
        amount = Fine.str_to_decimal(amount)
    except ConversionError as e:
        return jsonify({"error": str(e)}), 400
    
    try:
        LibrarianService(g.Session).issue_fine(
            user_id, amount, reason)
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Fine issued successfully"}), 200

@librarian.route("/add-book", methods=["POST"])
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
        return jsonify({"error": str(e)}), 400

    try:
        LibrarianService(g.Session).add_book(
            title, description, author, condition)
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Book added successfully"}), 200

@librarian.route("/search-books", methods=["POST"])
@requires_auth(AccountType.LIBRARIAN)
def search_books():
    data = request.json
    search = data.get("search")

    try:
        data = LibrarianService(g.Session).search_books(search)
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({
        "message": "Book search success",
        "data": data   
    }), 200

@librarian.route("/remove-book", methods=["POST"])
@requires_auth(AccountType.LIBRARIAN)
def remove_book():
    data = request.json
    book_id = data.get("book_id")

    try:
        book_id = Book.str_to_int(book_id)
    except ConversionError as e:
        return jsonify({"error": str(e)}), 400 

    try:
        data = LibrarianService(g.Session).remove_book(book_id)
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Book removed successfully"}), 200

@librarian.route("/update-book", methods=["POST"])
@requires_auth(AccountType.LIBRARIAN)
def update_book():
    data = request.json
    book_id = data.get("id")
    book_title = data.get("title")
    book_description = data.get("description")
    book_author = data.get("author")
    book_condition = data.get("condition")

    if book_condition:
        try:
            book_condition = Book.str_to_book_condition(book_condition)
        except ConversionError as e:
            return jsonify({"error": str(e)}), 400 

    new_book = Book(
        id=book_id,
        title=book_title,
        description=book_description,
        author=book_author,
        condition=book_condition
    )

    try:
        old_book = CommonService(g.Session).get_book(id=book_id)

        if len(old_book) == 0:
            return jsonify({"error": "Book {book_id} does not exist"}), 404 

        LibrarianService(g.Session).update_book(old_book[0], new_book)
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Book removed successfully"}), 200