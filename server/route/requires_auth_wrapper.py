from functools import wraps
from flask import jsonify, session, g
from server.model.tables import AccountType
from server.model.service.common_service import CommonService

def requires_auth(account_type):
    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            if (
                "session" not in session
                or session["session"]["account_type"] != account_type
                or not CommonService(g.Session).verify(
                    session["session"]["id"], 
                    session["session"]["account_type"]
                )
            ):
                return jsonify({"message": "Unauthorized"}), 401

            return method(*args, **kwargs)
        return wrapper
    return decorator