from functools import wraps

def transactional(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            with self.Session.begin() as self.session:
                return method(self, *args, **kwargs)
        except:
            raise Exception("Database operation failed")
        
    return wrapper