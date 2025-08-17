from server.exceptions import RecordNotFoundError
from server.model.repository.book_transaction_repository import BookTransactionRepository
from server.model.repository.fine_repository import FineRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountState, AccountType, BookTransaction, Fine, User
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
    ) -> list[tuple[
            User, 
            list[BookTransaction | None] | None, 
            list[Fine | None] | None]
        ]:
        result: list[tuple[
            User, 
            list[BookTransaction | None] | None, 
            list[Fine | None] | None]
        ] = []

        users = UserAccountRepository(self.session).get_user(
            id=id,
            name=name,
            email=email,
            account_type=account_type,
            account_state=account_state
        )

        if len(users) == 0:
            raise RecordNotFoundError()
        
        for user in users:
            transaction = BookTransactionRepository(self.session).get_transactions(
                user_id = user.id
            )

            fine = FineRepository(self.session).get_fine(
                user_id = user.id
            )
        
            result.append((
                user,
                transaction if len(transaction) != 0 else None, 
                fine if len(fine) != 0 else None, 
            ))

        return result

    @transactional
    def suspend_user(self, user: User) -> User:
        user.account_state = AccountState.SUSPENDED

        return user
    
    @transactional
    def reinstate_user(self, user: User) -> User:
        user.account_state = AccountState.ACTIVE

        return user