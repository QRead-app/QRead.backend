from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountState, AccountType, User
from server.model.repository.user_account_repository import UserAccountRepository
from sqlalchemy.exc import NoResultFound

class AdminService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def get_users(
        self, 
        id: int = None, 
        name: str = None,
        email: str = None,
        account_type: AccountType = None,
        account_state: AccountState = None
    ) -> list[User]:
        return UserAccountRepository(self.session).get_user(
            id=id,
            name=name,
            email=email,
            account_type=account_type,
            account_state=account_state
        )

    @transactional
    def suspend_user(self, user: User) -> User:
        user.account_state = AccountState.SUSPENDED

        return user
    
    @transactional
    def reinstate_user(self, user: User) -> User:
        user.account_state = AccountState.ACTIVE

        return user