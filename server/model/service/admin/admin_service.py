from server.exceptions import ConversionError, EmailAlreadyExistsError, RecordNotFoundError
from server.model.repository.app_settings_repository import AppSettingsRepository
from server.model.repository.book_transaction_repository import BookTransactionRepository
from server.model.repository.fine_repository import FineRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import AccountState, AccountType, AppSettings, BookTransaction, Fine, User
from server.model.repository.user_account_repository import UserAccountRepository
from sqlalchemy.exc import NoResultFound

from server.util.hasher import hasher
from server.util.mailer import mailer
from server.util.otp import otp

class AdminService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def register_librarian(self, email: str, redirect: str) -> None:
        user = UserAccountRepository(self.session).get_user(
            email = email
        )

        if len(user) > 0:
            raise EmailAlreadyExistsError()
        
        secret = otp.generate_librarian_secret(email)
        mailer.send_new_librarian(email, secret, redirect)

    @transactional
    def new_librarian(
        self,
        secret: str,
        name: str,
        password: str
    ) -> User:
        email = otp.verify_librarian_secret(secret)
        user = UserAccountRepository(self.session).get_user(
            email = email
        )

        if len(user) > 0:
            raise EmailAlreadyExistsError(email)
        
        password = hasher.hash(password)

        user = UserAccountRepository(self.session).insert_user(
            name, email, password, AccountType.LIBRARIAN)

        return user

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
    
    @transactional
    def delete_user(self, user: User) -> None:
        UserAccountRepository(self.session).delete_user(user)

    @transactional
    def update_setting(self, key: str, value: str) -> None:
        setting = AppSettingsRepository(self.session).get_setting(key)

        if len(setting) == 0:
            RecordNotFoundError()

        if (
            key == "reminder_every_x_days"
            or key == "reminder_x_days_before_due"
        ):
            try:
                AppSettings.str_to_int(value)
            except ConversionError:
                raise ConversionError()
            
        setting[0].value = value