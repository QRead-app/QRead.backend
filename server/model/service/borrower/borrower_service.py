from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountType
from server.model.repository.user_account_repository import UserAccountRepository
from sqlalchemy.exc import NoResultFound

class BorrowerService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def register(self, name: str, email: str, password: str) -> None:
        user_repo = UserAccountRepository(self.session)

        # Check email duplication
        duplicate = True
        try:
            user_repo.get_user_by_email(email)
        except NoResultFound:
            duplicate = False
        if duplicate:
            raise Exception("Email is duplicated")

        user_repo.insert_user(name, email, password, AccountType.BORROWER)