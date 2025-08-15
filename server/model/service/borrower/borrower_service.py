from datetime import datetime, timedelta
from server.exceptions import BookBorrowingError, DatabaseError, EmailAlreadyExistsError, RecordNotFoundError
from server.model.repository.book_return_repository import BookReturnRepository
from server.model.repository.fine_repository import FineRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountType, Book, BookReturn, BookTransaction, Fine, User
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
    def borrow_book(self, user_id: int, book_ids: list[int]) -> list[Book]:
        transaction_repo = BookTransactionRepository(self.session)
        book_repo = BookRepository(self.session)
        books_borrowed: list[Book] = []
        
        for book_id in book_ids:

            # Check if book exist
            book_check = book_repo.get_book(id=book_id)

            if len(book_check) == 0:
                raise RecordNotFoundError(book_id)
            
            if len(book_check) > 1:
                raise DatabaseError()

            # Check if book is borrowed
            if book_check[0].on_loan:
                raise BookBorrowingError(book_id)
            
            book = transaction_repo.insert_transaction(
                user_id = user_id,
                book_id = book_id,
                due_date = datetime.now() + timedelta(days=14)
            )
            book_check[0].on_loan = True
            books_borrowed.append(book)

        return books_borrowed
    
    @transactional
    def get_borrowed_books(self, user_id: int) -> list[tuple[Book, BookTransaction]]:
        transaction_repo = BookTransactionRepository(self.session)
        book_repo = BookRepository(self.session)

        transaction_history = transaction_repo.get_transactions(
            user_id = user_id,
            returned = False
        )

        if len(transaction_history) == 0:
            raise RecordNotFoundError()

        result: list[tuple[Book, BookTransaction]] = []

        for transaction in transaction_history:
            book = book_repo.get_book(id = transaction.book_id)

            if len(book) == 0:
                raise RecordNotFoundError(transaction.book_id)
            
            if len(book) > 1:
                raise DatabaseError()
            
            result.append((book[0], transaction))

        return result
    
    @transactional
    def get_borrow_history(self, user_id: int) -> list[tuple[Book, BookTransaction, BookReturn]]:
        transaction_repo = BookTransactionRepository(self.session)
        book_repo = BookRepository(self.session)
        return_repo = BookReturnRepository(self.session)

        transaction_history = transaction_repo.get_transactions(
            user_id = user_id
        )

        if len(transaction_history) == 0:
            raise RecordNotFoundError({
                "type": "transaction_history"
            })

        result: list[tuple[Book, BookTransaction]] = []

        for transaction in transaction_history:
            book = book_repo.get_book(id = transaction.book_id)

            if len(book) == 0:
                raise RecordNotFoundError({
                    "type": "book",
                    "data": transaction.book_id
                })
            
            if len(book) > 1:
                raise DatabaseError()
            
            return_record = return_repo.get_book_return(
                book_transaction_id = transaction.id
            )

            if len(return_record) == 0:
                raise RecordNotFoundError({
                "type": "return",
                "data": transaction.id
            })
            
            if len(book) > 1:
                raise DatabaseError()
            
            result.append((book[0], transaction, return_record))

        return result
    
    @transactional
    def get_fines(self, user_id: int) -> tuple[list[Fine], list[Book]]:
        fine_repo = FineRepository(self.session)
        transaction_repo = BookTransactionRepository(self.session)
        book_repo = BookRepository(self.session)

        fines = fine_repo.get_fine(
            user_id = user_id, paid = False
        )

        if len(fines) == 0:
            raise RecordNotFoundError()
        
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
    def pay_fine(self, id: int) -> list[Book]:
        fine_repo = FineRepository(self.session)

        fine = fine_repo.get_fine(
            id = id, paid = False
        )

        if len(fine) == 0:
            raise RecordNotFoundError(f"Fine {id} not found")
        
        if len(fine) > 1:
            raise DatabaseError("Database error")
        
        fine[0].paid = True
        
        return fine