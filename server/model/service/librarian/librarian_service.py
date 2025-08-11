from decimal import Decimal
from server.model.repository.book_repository import BookRepository
from server.model.repository.fine_repository import FineRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import Book, BookCondition, Fine

class LibrarianService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def issue_fine(self, user_id: int, transaction_id: int, amount: Decimal, reason: str) -> Fine:
        fine_repo = FineRepository(self.session)

        fine = fine_repo.insert_fine(user_id, transaction_id, amount, reason)

        return fine
    
    @transactional
    def add_book(self, title: str, description: str, author: str, condition: BookCondition) -> Book:
        book = BookRepository(self.session).insert_book(
            title, description, author, condition)
        
        return book
    
    @transactional
    def search_books(self, search: str) -> list[Book]:
        books = BookRepository(self.session).search_books(search)

        return books
    
    @transactional
    def remove_book(self, book_id: int) -> None:
        book_repo = BookRepository(self.session)

        book = book_repo.get_book(id=book_id)[0]
        book_repo.delete_book(book)
    
    @transactional
    def update_book(self, old_book: Book, new_book: Book) -> None:
        for attr in ("title", "description", "author", "condition"):
            val = getattr(new_book, attr)
            if val is not None:
                setattr(old_book, attr, val)