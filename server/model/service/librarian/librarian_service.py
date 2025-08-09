from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountType, User
from server.model.repository.user_account_repository import UserAccountRepository
from server.exceptions import EmailAlreadyExistsError

class LibrarianService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def register(self, email: str, password: str) -> User:
        user_repo = UserAccountRepository(self.session)

        result = user_repo.get_user(email = email, 
                                    password = password, 
                                    account_type = AccountType.ADMIN)
        if len(result) > 0:
            raise EmailAlreadyExistsError("The email provided is already registered")
        
        
        return True