class ServiceError(Exception):
    pass

class EmailAlreadyExistsError(ServiceError):
    pass

class BookBorrowingError(ServiceError):
    pass

class RecordNotFoundError(ServiceError):
    pass

class IncorrectCredentialsError(ServiceError):
    pass

class DatabaseError(ServiceError):
    pass

class ConversionError(ServiceError):
    pass