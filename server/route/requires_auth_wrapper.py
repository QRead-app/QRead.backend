from functools import wraps
from flask import jsonify, session, g
from server.model.tables import AccountType
from server.model.service.common_service import CommonService

def requires_auth(method):
    @wraps(method)
    def wrapper(account_type: AccountType, *args, **kwargs):
        if (
            "session" not in session or
            session["session"]["account_type"] != account_type or
            not CommonService(g.Session).verify(session["session"]["email"], session["session"]["account_type"])
        ):
            return jsonify({"message": "Unauthorised"}), 401
        
        return method(*args, **kwargs)
        
    return wrapper