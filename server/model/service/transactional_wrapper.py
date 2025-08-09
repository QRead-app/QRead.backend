from functools import wraps
from server.exceptions import DatabaseError

def transactional(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            with self.Session.begin() as self.session:
                return method(self, *args, **kwargs)
        except:
            raise DatabaseError("Database operation failed")
        
    return wrapper