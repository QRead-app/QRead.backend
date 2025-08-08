from ..tables import User, AccountType
from .base_repository import BaseRepository
from sqlalchemy import Row, select
from sqlalchemy.orm import Session

class UserAccountRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_user_by_id(self, id: int) -> User|None:
        return self.session.get(User, id)
    
    def get_users_by_name(self, name: str) -> Row[User]|None:
        return self.session.execute(
            select(User)
                .where(User.name == name)
        ).all()
    
    def get_user_by_email(self, email: str) -> Row[User]|None:
        return self.session.execute(
            select(User)
                .where(User.email == email)
        ).one()

    def insert_user(self, name: str, email: str, password: str, type: AccountType) -> User:
        user = User(name = name, email = email, password = password, account_type = type)
        self.session.add(user)

        return user

    def delete_user(self, user: User) -> None:
        self.session.delete(user)    