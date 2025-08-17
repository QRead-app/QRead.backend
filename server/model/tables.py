from decimal import Decimal
import enum
import re

from typing import List, Optional
from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.types import TIMESTAMP, NUMERIC
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from server.exceptions import ConversionError

class AccountType(enum.Enum):
    ADMIN = 1
    LIBRARIAN = 2
    BORROWER = 3

class BookCondition(enum.Enum):
    NEW = 1
    LIKE_NEW = 2
    VERY_GOOD = 3
    GOOD = 4
    FAIR = 5
    WORN = 6
    DAMAGED = 7
    UNUSABLE = 8

class AccountState(enum.Enum):
    ACTIVE = 1,
    SUSPENDED = 2

class Base(DeclarativeBase):
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
    
    @staticmethod
    def str_to_int(str: str) -> int:
        try:
            return int(str)
        except ValueError:
            raise ConversionError(f"Error converting {str} to int")
        
    @staticmethod
    def str_to_decimal(str: str) -> Decimal:
        try:
            return Decimal(str)
        except ValueError:
            raise ConversionError(f"Error converting {str} to Decimal")

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    account_type: Mapped[AccountType]
    account_state: Mapped[AccountState]

    fines: Mapped[List["Fine"]] = relationship(back_populates="user")
    transactions: Mapped[List["BookTransaction"]] = relationship(back_populates="user")
    book_returns: Mapped[List["BookReturn"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"""
            id: {self.id}, 
            name: {self.name}, 
            email: {self.email}, 
            password: {self.password}, 
            account_type: {self.account_type},
            account_state: {self.account_state}
        """
    
    def to_dict(self):
        dict = super().to_dict()
        dict["account_type"] = self.account_type.name
        dict["account_state"] = self.account_state.name

        return dict
    
    @staticmethod
    def is_email(email: str) -> bool:
        return re.search("^.+@.+[.].+$", email) != None

    @staticmethod
    def str_to_account_type(str: str) -> AccountType:
        try:
            return AccountType[str.upper()]
        except KeyError:
            raise ConversionError(f"Error converting {str} to AccountType ENUM")
        
    @staticmethod
    def str_to_account_state(str: str) -> AccountState:
        try:
            return AccountState[str.upper()]
        except KeyError:
            raise ConversionError(f"Error converting {str} to AccountState ENUM")

class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[Optional[str]]
    author: Mapped[str]
    condition: Mapped[BookCondition]
    on_loan: Mapped[bool] = mapped_column(server_default="False")

    transactions: Mapped[List["BookTransaction"]] = relationship(back_populates="book")

    def __repr__(self):
        return f"""
            id: {self.id}, 
            title: {self.title}, 
            description: {self.description}, 
            author: {self.author}, 
            condition: {self.condition},
            on_loan: {self.on_loan}
        """
    
    def to_dict(self):
        dict = super().to_dict()
        dict["condition"] = self.condition.name

        return dict
    
    @staticmethod
    def str_to_book_condition(str: str) -> BookCondition:
        try:
            return BookCondition[str.upper()]
        except KeyError:
            raise ConversionError(f"Error converting {str} to BookCondition ENUM")

class Fine(Base):
    __tablename__ = "fine"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey("user_account.id"), nullable=False)
    transaction_id = mapped_column(ForeignKey("book_transaction.id"), nullable=False)
    reason: Mapped[str]
    amount = mapped_column(NUMERIC(precision=2), nullable=False)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    paid: Mapped[bool] = mapped_column(server_default="False")

    user: Mapped["User"] = relationship(back_populates="fines")
    transaction: Mapped["BookTransaction"] = relationship(back_populates="fine")

    def __repr__(self):
        return f"""
            id: {self.id}, 
            user_id: {self.user_id}, 
            transaction_id: {self.transaction_id}, 
            reason: {self.reason}, 
            amount: {self.amount}, 
            date: {self.date}, 
            paid: {self.paid}
        """

class BookTransaction(Base):
    __tablename__ = "book_transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey("user_account.id"), nullable=False)
    book_id = mapped_column(ForeignKey("book.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    due: Mapped[datetime]
    returned: Mapped[bool] = mapped_column(server_default="False")

    user: Mapped["User"] = relationship(back_populates="transactions")
    book: Mapped["Book"] = relationship(back_populates="transactions")
    fine: Mapped["Fine"] = relationship(back_populates="transaction")
    book_return: Mapped["BookReturn"] = relationship(back_populates="book_transaction")

    def __repr__(self):
        return f"""
            id: {self.id}, 
            user_id: {self.user_id}, 
            book_id: {self.book_id},
            date: {self.date}, 
            due: {self.due}
        """
    
class BookReturn(Base):
    __tablename__ = "book_return"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    book_transaction_id = mapped_column(ForeignKey("book_transaction.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    librarian_id = mapped_column(ForeignKey("user_account.id"), nullable=False)

    book_transaction: Mapped["BookTransaction"] = relationship(back_populates="book_return")
    user: Mapped["User"] = relationship(back_populates="book_returns")

    def __repr__(self):
        return f"""
            id: {self.id}, 
            book_transaction_id: {self.book_transaction_id},
            date: {self.date}, 
            librarian_id: {self.librarian_id}
        """
    
class AppSettings(Base):
    __tablename__ = "app_settings"

    key: Mapped[str]
    value: Mapped[str]