from flask import Blueprint, g, jsonify, request, session
from server.exceptions import BookBorrowingError, ConversionError, DatabaseError, EmailAlreadyExistsError, RecordNotFoundError
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

    if name is None:
        return jsonify({"error": "Missing name field"}), 400
    if email is None:
        return jsonify({"error": "Missing email field"}), 400
    if password is None:
        return jsonify({"error": "Missing password field"}), 400

    if not User.is_email(email):
        return jsonify({"error": f"Invalid email {email}"}), 400
    
    try:
        BorrowerService(g.Session).register(name, email, password)
    except EmailAlreadyExistsError as e:
        return jsonify({"error": f"Email {email} is already registered"}), 400

    return jsonify({"message": "Registered"}), 200

@borrower.route("/borrow", methods=["POST"])
@requires_auth(AccountType.BORROWER)
def borrow():
    data = request.json
    book_ids = data.get("book_ids")
    
    if book_ids is None:
        return jsonify({"error": "Missing book_ids field"}), 400
    
    for n in range(len(book_ids)):
        try:
            book_ids[n] = Book.str_to_int(book_ids[n])
        except ConversionError:
            return jsonify({"error": f"Invalid Book id {book_ids[n]}"}), 400

    try:
        BorrowerService(g.Session).borrow_book(
            session["session"]["id"], book_ids)
    except RecordNotFoundError as e:
        return jsonify({"error": f"Book id {e} not found"}), 400
    except BookBorrowingError as e:
        return jsonify({"error": f"Book id {e} has already been borrowed"}), 400
    
    return jsonify({"message": "Book(s) borrowed successfully"}), 200

@borrower.route("/get-borrowed-books", methods=["GET"])
@requires_auth(AccountType.BORROWER)
def get_borrowed_books():
    borrowed_books: list[Book] = []

    try:
        borrowed_books = BorrowerService(g.Session).get_borrowed_books(
            session["session"]["id"])
    except RecordNotFoundError:
        return jsonify({"message": "No books found"}), 200
    
    borrowed_books_dict = []

    for book in borrowed_books:
        borrowed_books_dict.append(book.to_dict())

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
    except RecordNotFoundError:
        return jsonify({"message": "No fines found"}), 200
    
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
        return jsonify({"error": "Missing fine_id field"}), 400
    
    try:
        fine_id = Fine.str_to_int(fine_id)
    except ConversionError:
        return jsonify({"error": f"Invalid fine id {fine_id}"}), 400 

    try:
        BorrowerService(g.Session).pay_fine(fine_id)
    except RecordNotFoundError as e:
        return jsonify({"error": f"Fine id {fine_id} not found"}), 404

    return jsonify({"message": "Fine paid successfully"}), 200