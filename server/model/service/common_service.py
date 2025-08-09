from server.exceptions import DatabaseError, IncorrectCredentialsError
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountType, User
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
                return IncorrectCredentialsError("Authentication failed")
            if len(user) > 1:
                return DatabaseError("Database record error")
            
            return user[0]

    @transactional
    def verify(self, email: str, account_type: AccountType) -> bool:
            user_repo = UserAccountRepository(self.session)

            result = user_repo.get_user(email = email, 
                                        account_type = account_type)
            
            if len(result) == 0:
                return False
            
            return True