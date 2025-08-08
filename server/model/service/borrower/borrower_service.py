from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountType
from server.model.repository.user_account_repository import UserAccountRepository
from sqlalchemy.exc import NoResultFound

class BorrowerService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def authenticate(self, email: str, password: str) -> bool:
            user_repo = UserAccountRepository(self.session)

            try:
                user_repo.get_user_by_email_password(email, password, AccountType.ADMIN)
            except NoResultFound: 
                return False
            
            return True