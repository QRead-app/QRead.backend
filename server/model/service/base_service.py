from server.model.repository.book_repository import BookRepository


class BaseService:
    def __init__(self, Session):
        self.Session = Session
        self.book_repo = BookRepository()