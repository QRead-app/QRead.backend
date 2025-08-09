class ServiceError(Exception):
    pass

class EmailAlreadyExistsError(ServiceError):
    pass

class BookAlreadyBorrowedError(ServiceError):
    pass

class IncorrectCredentialsError(ServiceError):
    pass

class DatabaseError(ServiceError):
    pass