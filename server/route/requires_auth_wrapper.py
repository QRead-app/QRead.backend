from functools import wraps
from flask import jsonify, session, g
from server.model.tables import AccountType
from server.model.service.common_service import CommonService

def requires_auth(account_type: AccountType | None):
    def auth_type_check(type: AccountType | None, check: AccountType) -> bool:
        if type is not None:
            return type == check
        
        return type in AccountType

    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            auth_type = None
            
            if account_type is not None:
                auth_type = account_type.name
                
            if (
                "session" not in session
                or auth_type_check(session["session"]["account_type"], auth_type)
                or not CommonService(g.Session).verify(
                    session["session"]["id"], 
                    session["session"]["account_type"]
                )
            ):
                return jsonify({"error": "Unauthorized"}), 401

            return method(*args, **kwargs)
        return wrapper
    return decorator