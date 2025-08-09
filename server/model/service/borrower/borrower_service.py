from datetime import datetime, timedelta
from typing import Tuple
from server.exceptions import BookBorrowingError, EmailAlreadyExistsError
from server.model.repository.fine_repository import FineRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountType, Book, BookTransaction, Fine, User
from server.model.repository.user_account_repository import UserAccountRepository
from server.model.repository.book_repository import BookRepository
from server.model.repository.book_transaction_repository import BookTransactionRepository

class BorrowerService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def register(self, name: str, email: str, password: str) -> User:
        user_repo = UserAccountRepository(self.session)

        # Check email duplication
        result = user_repo.get_user(email = email)

        if len(result) > 0:
            raise EmailAlreadyExistsError("The email provided is already registered")

        user = user_repo.insert_user(name, email, password, AccountType.BORROWER)

        return user

    @transactional
    def borrow_book(self, id: str, book_ids: list[int]) -> list[Book]:
        transaction_repo = BookTransactionRepository(self.session)
        books_borrowed: list[Book] = []

        for book_id in book_ids:
            # Check if book is borrowed
            result = transaction_repo.get_transactions(
                user_id = id, 
                book_id = book_id,
                returned = False
            )

            if result is not None:
                raise BookBorrowingError(
                    f"{book_id} has already been borrowed or does not exist")
            
            book = transaction_repo.insert_transaction(
                user_id = id,
                book_id = book_id,
                due_date = datetime.now() + timedelta(days=14)
            )
            books_borrowed.append(book)

        return books_borrowed
    
    @transactional
    def get_borrowed_book(self, id: str) -> list[Book]:
        transaction_repo = BookTransactionRepository(self.session)
        book_repo = BookRepository(self.session)

        borrowed_book_transactions = transaction_repo.get_transactions(
            user_id = id, returned = False
        )

        if borrowed_book_transactions is None:
            return []

        borrowed_books: list[Book] = []
        for book in borrowed_books:
            book_obj = book_repo.get_book(id = book.id)
            borrowed_books.append(book_obj)

        return borrowed_books
    
    @transactional
    def get_fines(self, id: str) -> Tuple[list[Fine], list[Book]]:
        fine_repo = FineRepository(self.session)
        transaction_repo = BookTransactionRepository(self.session)
        book_repo = BookRepository(self.session)

        fines = fine_repo.get_fine(
            user_id = id, paid = False
        )

        if fines is None:
            return []
        
        transactions: list[BookTransaction] = []
        for fine in fines:
            transaction = transaction_repo.get_transactions(
                id = fine.transaction_id)
            transactions.append(transaction)

        books: list[Book] = []
        for transaction in transactions:
            book = book_repo.get_book(
                id = transaction.book_id
            )
            books.append(book)
        
        return fines, books
    
    @transactional
    def pay_fine(self, id: str) -> list[Book]:
        fine_repo = FineRepository(self.session)

        fines = fine_repo.get_fine(
            user_id = id, paid = False
        )

        if fines is None:
            return []
        
        
        
        return fines