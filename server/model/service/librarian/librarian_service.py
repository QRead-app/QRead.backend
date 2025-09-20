from decimal import Decimal
from server.exceptions import BookBorrowingError, DatabaseError, RecordNotFoundError
from server.model.repository.book_repository import BookRepository
from server.model.repository.book_return_repository import BookReturnRepository
from server.model.repository.book_transaction_repository import BookTransactionRepository
from server.model.repository.user_account_repository import UserAccountRepository
from server.model.repository.fine_repository import FineRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import Book, BookCondition, BookReturn, Fine, User

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

        if len(books) == 0:
            raise RecordNotFoundError()

        return books
    
    @transactional
    def remove_book(self, book_id: int) -> None:
        book_repo = BookRepository(self.session)

        book = book_repo.get_book(id=book_id)

        if len(book) == 0:
            raise RecordNotFoundError()
        
        if len(book) > 1:
            raise DatabaseError()

        book_repo.delete_book(book)
    
    @transactional
    def update_book(self, old_book: Book, new_book: Book) -> Book:
        for attr in ("title", "description", "author", "condition", "on_loan"):
            val = getattr(new_book, attr)
            if val is not None:
                setattr(old_book, attr, val)

        return old_book
    
    @transactional
    def return_book(self, librarian_id: int, book_id: int) -> BookReturn:
        return_repo = BookReturnRepository(self.session)
        transaction_repo = BookTransactionRepository(self.session)
        book_repo = BookRepository(self.session)

        book = book_repo.get_book(
            id = book_id
        )

        if len(book) == 0:
            raise RecordNotFoundError(book_id)
        
        if len(book) > 1:
            raise DatabaseError()

        transaction = transaction_repo.get_transactions(
            book_id = book_id,
            returned = False
        )

        if len(transaction) == 0:
            raise BookBorrowingError()
        
        if len(transaction) > 1:
            raise DatabaseError()
        
        book[0].on_loan = False
        transaction[0].returned = True

        bookreturn = return_repo.insert_book_return(
            transaction[0].id,
            librarian_id
        )

        return bookreturn
    
    @transactional
    def update_user(
        self, 
        id: int = None, 
        name: str = None,
        email: str = None,
        password: str = None,
        newpassword: str = None
    ) -> User:
        user = UserAccountRepository(self.session).get_user(
            id=id,
            password = password
        )

        if len(user) == 0:
            raise RecordNotFoundError()
        
        for field, val in {
            "name": name,
            "email": email,
            "password": newpassword,
        }.items():
            if val is not None:
                setattr(user, field, val)

        return user