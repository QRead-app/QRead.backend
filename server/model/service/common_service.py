from server.exceptions import AuthorizationError, DatabaseError, IncorrectCredentialsError, RecordNotFoundError
from server.model.repository.book_repository import BookRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountState, AccountType, Book, BookCondition, BookTransaction, User
from server.model.repository.user_account_repository import UserAccountRepository
from server.model.repository.book_transaction_repository import BookTransactionRepository
from server.util.mailer import mailer
from server.util.otp import otp
from server.util.hasher import hasher

class CommonService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def authenticate(self, email: str, password: str, account_type: AccountType) -> User:
        user_repo = UserAccountRepository(self.session)

        user = user_repo.get_user(
            email = email, 
            account_type = account_type
        )
        
        if len(user) > 1:
            raise DatabaseError("Database record error")
        
        if len(user) == 0:
            raise IncorrectCredentialsError("Authentication failed")
        
        if not hasher.verify(user[0].password, password):
            raise IncorrectCredentialsError("Authentication failed")
        
        if hasher.need_rehash(user[0].password):
            user[0].password = hasher.hash(password)
        
        user = user[0]

        if user.account_state == AccountState.SUSPENDED:
            raise AuthorizationError("Suspended")
        
        if user.account_state == AccountState.DELETED:
            raise AuthorizationError("Deleted")

        onetimepass = otp.generate_otp(user.id)
        mailer.send_otp(user.email, onetimepass)

        return user
    
    @transactional
    def verify_otp(self, id:str, onetimepass: str) -> bool:
        if otp.verify_otp(id, onetimepass):
            return UserAccountRepository(self.session).get_user(
                id=id
            )[0]
        return False

    @transactional
    def verify(self, id: str, account_type: AccountType) -> bool:
        user_repo = UserAccountRepository(self.session)

        result = user_repo.get_user(id = id, 
                                    account_type = account_type)
        
        if len(result) == 0:
            return False
        
        return True
    
    @transactional
    def get_book(
        self, 
        id: int | None = None, 
        title: str | None = None, 
        description: str | None = None, 
        author: str | None = None, 
        condition: BookCondition | None = None,
        on_loan: bool | None = None
    ) -> list[Book]:
        books = BookRepository(self.session).get_book(
            id,
            title,
            description,
            author,
            condition,
            on_loan
        )

        if len(books) == 0:
            raise RecordNotFoundError()

        return books
    
    @transactional
    def get_transaction(self, book_id: int) -> BookTransaction:
        transaction = BookTransactionRepository(self.session).get_transactions(
            book_id=book_id
        )
        
        if len(transaction) == 0:
            raise RecordNotFoundError()
        
        # if len(transaction) > 1:
        #     raise DatabaseError()
        
        return transaction[0];
    
    @transactional
    def forgot_password(self, email: str, redirect_url: str) -> None:
        user = UserAccountRepository(self.session).get_user(
            email = email
        )
        
        if len(user) == 0:
            raise RecordNotFoundError()
        
        if len(user) > 1:
            raise DatabaseError()
        
        user = user[0]

        # if user.account_type == AccountType.ADMIN:
        #     raise AuthorizationError()
        
        secret = otp.generate_forgot_password_otp(user.id)
        mailer.send_forgot_password(user.email, secret, redirect_url)

    @transactional
    def reset_password(self, secret: str, password: str) -> None:
        id = otp.verify_forgot_password(secret)

        user = UserAccountRepository(self.session).get_user(
            id = id
        )

        if len(user) == 0:
            raise RecordNotFoundError()
        
        if len(user) > 1:
            raise DatabaseError()
        
        user[0].password = hasher.hash(password)