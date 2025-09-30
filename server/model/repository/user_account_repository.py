from ..tables import AccountState, User, AccountType
from .base_repository import BaseRepository
from sqlalchemy import select, text
from sqlalchemy.orm import Session

class UserAccountRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_user(
        self, 
        id: int | None = None, 
        name: str | None = None, 
        email: str | None = None,
        account_type: AccountType | None = None,
        account_state: AccountState | None = None
    ) -> list[User]:
        stmt = select(User)

        filters = []
        if id is not None:
            filters.append(User.id == id)
        if name is not None:
            filters.append(User.name == name)
        if email is not None:
            filters.append(User.email == email)
        if account_type is not None:
            filters.append(User.account_type == account_type)
        if account_state is not None:
            filters.append(User.account_state == account_state)

        if filters: 
            stmt = stmt.where(*filters)

        return self.session.execute(stmt).scalars().all()


    def insert_user(
            self, 
            name: str, 
            email: str, 
            password: str, 
            type: AccountType,
            state: AccountState = AccountState.ACTIVE
        ) -> User:
        user = User(
            name = name, 
            email = email, 
            password = password, 
            account_type = type,
            account_state = state
        )
        self.session.add(user)

        return user

    def delete_user(self, user: User) -> None:
        self.session.delete(user)   

    def truncate_table(self) -> None:
        self.session.execute(text("TRUNCATE TABLE user_account RESTART IDENTITY CASCADE"))