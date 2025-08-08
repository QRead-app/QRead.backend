from flask import Blueprint, g, jsonify, request
from server.utils.sanitization import is_email
from server.model.service.borrower.borrower_service import BorrowerService

borrower = Blueprint('borrower', __name__, url_prefix="/borrower")

@borrower.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data["name"]
    email = data["email"]
    password = data["password"]

    if not is_email(email):
        return jsonify({"message": "Invalid Email"}), 400
    
    try:
        BorrowerService(g.Session).register(name, email, password)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Registered"}), 200