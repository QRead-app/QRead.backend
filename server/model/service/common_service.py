from server.exceptions import DatabaseError, IncorrectCredentialsError, RecordNotFoundError
from server.model.repository.book_repository import BookRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountType, Book, BookCondition, User
from server.model.repository.user_account_repository import UserAccountRepository

class CommonService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def authenticate(self, email: str, password: str, account_type: AccountType) -> User:
        user_repo = UserAccountRepository(self.session)

        user = user_repo.get_user(email = email, password = password, 
                                    account_type = account_type)
        
        if len(user) == 0:
            raise IncorrectCredentialsError("Authentication failed")
        if len(user) > 1:
            raise DatabaseError("Database record error")
        
        return user[0]

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