from ..tables import User, AccountType
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
        password: str | None = None, 
        account_type: AccountType | None = None,
    ) -> list[User]:
        stmt = select(User)

        filters = []
        if id is not None:
            filters.append(User.id == id)
        if name is not None:
            filters.append(User.name == name)
        if email is not None:
            filters.append(User.email == email)
        if password is not None:
            filters.append(User.password == password)
        if account_type is not None:
            filters.append(User.account_type == account_type)

        if filters: 
            stmt = stmt.where(*filters)

        return self.session.execute(stmt).scalars().all()


    def insert_user(self, name: str, email: str, password: str, type: AccountType) -> User:
        user = User(name = name, email = email, password = password, account_type = type)
        self.session.add(user)

        return user

    def delete_user(self, user: User) -> None:
        self.session.delete(user)   

    def truncate_table(self) -> None:
        self.session.execute(text("TRUNCATE TABLE user_account CASCADE"))