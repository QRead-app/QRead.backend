from flask import Blueprint, g, jsonify, request, session
from server.exceptions import BookBorrowingError, DatabaseError, EmailAlreadyExistsError, RecordNotFoundError
from server.model.tables import AccountType, Book, Fine, User
from server.model.service.borrower.borrower_service import BorrowerService
from server.route.requires_auth_wrapper import requires_auth

borrower = Blueprint('borrower', __name__, url_prefix="/borrower")

@borrower.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if (
        name is None
        or email is None
        or password is None
    ):
        return jsonify({"error": "Missing fields"}), 400

    if not User.is_email(email):
        return jsonify({"error": "Invalid Email"}), 400
    
    try:
        BorrowerService(g.Session).register(name, email, password)
    except EmailAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Registered"}), 200

@borrower.route("/borrow", methods=["POST"])
@requires_auth(AccountType.BORROWER)
def borrow():
    data = request.json
    book_ids = data.get("books")
    
    if book_ids is None:
        return jsonify({"error": "Missing field"}), 400
    
    try:
        BorrowerService(g.Session).borrow_book(
            session["session"]["id"], book_ids)
    except BookBorrowingError as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Book(s) borrowed successfully"}), 200

@borrower.route("/get-borrowed-books", methods=["GET"])
@requires_auth(AccountType.BORROWER)
def get_borrowed_books():
    borrowed_books: list[Book] = []
    try:
        borrowed_books = BorrowerService(g.Session).get_borrowed_books(
            session["session"]["id"])
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    if len(borrowed_books) == 0:
        return jsonify({"message": "No books found"}), 204
    
    borrowed_books_dict = []
    for book in borrowed_books:
        borrowed_books_dict.append(book.to_dict)

    return jsonify({
        "message": "Borrowed book(s) retrieved",
        "data": borrowed_books_dict
    }), 200

@borrower.route("/get-fines", methods=["GET"])
@requires_auth(AccountType.BORROWER)
def get_fines():
    fines: list[Fine] = []
    books: list[Book] = []

    try:
        fines, books = BorrowerService(g.Session).get_fines(
            session["session"]["id"])
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
    if len(fines) == 0:
        return jsonify({"message": "No fines found"}), 204
    
    fines_dict = []
    for n in range(len(fines)):
        fine_dict = fines[n].to_dict()
        book_dict = books[n].to_dict()

        fine_dict["book"] = book_dict
        fines_dict.append(fine_dict)
        
    return jsonify({
        "message": "Fine(s) retrieved",
        "data": fine_dict
    }), 200

@borrower.route("/pay-fine", methods=["POST"])
@requires_auth(AccountType.BORROWER)
def pay_fine():
    data = request.json
    fine_id = data.get("fine_id")

    if fine_id is None:
        return jsonify({"error": "Missing field"}), 400

    try:
        BorrowerService(g.Session).pay_fine(fine_id)
    except RecordNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Fine paid successfully",
    }), 200