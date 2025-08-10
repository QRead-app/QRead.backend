from functools import wraps
from server.exceptions import DatabaseError
from  sqlalchemy.exc import DBAPIError

def transactional(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            with self.Session.begin() as self.session:
                self.session.expire_on_commit = False
                return method(self, *args, **kwargs)
        except DBAPIError:
            raise DatabaseError("Database operation failed")
        
    return wrapper