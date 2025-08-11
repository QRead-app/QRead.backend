from flask import Blueprint, g, jsonify, request

from server.exceptions import ConversionError, DatabaseError
from server.model.service.librarian.librarian_service import LibrarianService
from server.model.tables import AccountType, Fine
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

