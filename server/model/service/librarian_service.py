
from decimal import Decimal
from server.exceptions import BookBorrowingError, DatabaseError, IncorrectCredentialsError, RecordNotFoundError
from server.model.repository.book_repository import BookRepository
from server.model.repository.book_return_repository import BookReturnRepository
from server.model.repository.book_transaction_repository import BookTransactionRepository
from server.model.repository.user_account_repository import UserAccountRepository
from server.model.repository.fine_repository import FineRepository
from server.model.service.common_service import CommonService
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import Book, BookCondition, BookReturn, Fine, User
from server.util.hasher import hasher

class LibrarianService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def issue_fine(self, user_id: int, book_id: int, amount: Decimal, reason: str) -> Fine:
        fine_repo = FineRepository(self.session)
        transaction_repo = BookTransactionRepository(self.session)

        transaction = transaction_repo.get_transactions(user_id=user_id, book_id=book_id)

        if (len(transaction) == 0):
            raise RecordNotFoundError()
        
        fine = fine_repo.insert_fine(user_id, transaction[0].id, amount, reason)

        return fine
    
    @transactional
    def add_book(self, title: str, description: str, author: str, condition: BookCondition, image: str) -> Book:
        book = BookRepository(self.session).insert_book(
            title, description, author, condition, image)
        
        return book
    
    @transactional
    def search_books(self, search: str) -> list[Book]:
        books = BookRepository(self.session).search_books(search)

        if len(books) == 0:
            raise RecordNotFoundError()
        
        transactions = []
        for book in books:
            transactions.append(BookTransactionRepository(self.sessoin)
                                .get_transactions(
                                    book_id=books[books[0].id]
                                ))

        return books, transactions
    
    @transactional
    def remove_book(self, book_id: int) -> None:
        book_repo = BookRepository(self.session)

        book = book_repo.get_book(id=book_id)

        if len(book) == 0:
            raise RecordNotFoundError()
        
        if len(book) > 1:
            raise DatabaseError()

        book_repo.delete_book(book[0])
    
    @transactional
    def update_book(self, id: int, new_book: Book) -> Book:
        old_book = BookRepository(self.session).get_book(id)[0]

        for attr in ("title", "description", "author", "condition", "on_loan", "image"):
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
        
        if book[0].on_loan == True:
            raise BookBorrowingError()

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
            id=id
        )

        if len(user) == 0:
            raise RecordNotFoundError()
        
        user = user[0]

        if not hasher.verify(user.password, password):
            raise IncorrectCredentialsError("Authentication failed")
        
        for field, val in {
            "name": name,
            "email": email,
            "password": hasher.hash(newpassword),
        }.items():
            if val is not None:
                setattr(user, field, val)

        return user
