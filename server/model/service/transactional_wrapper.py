from functools import wraps

def transactional(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self.Session.begin() as self.session:
            return method(self, *args, **kwargs)
        
    return wrapper