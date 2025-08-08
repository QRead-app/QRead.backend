import enum

from typing import List, Optional
from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.types import TIMESTAMP, NUMERIC
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

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

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    account_type: Mapped[AccountType]

    fines: Mapped[List["Fine"]] = relationship(back_populates="user")
    transactions: Mapped[List["BookTransaction"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}, email: {self.email}, password: {self.password}, account_type: {self.account_type}"

class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[Optional[str]]
    author: Mapped[str]
    condition: Mapped[BookCondition]

    transactions: Mapped[List["BookTransaction"]] = relationship(back_populates="book")

    def __repr__(self):
        return f"id: {self.id}, title: {self.title}, description: {self.description}, author: {self.author}, condition: {self.condition}"

class Fine(Base):
    __tablename__ = "fine"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey("user_account.id"), nullable=False)
    transaction_id = mapped_column(ForeignKey("book_transaction.id"), nullable=False)
    amount = mapped_column(NUMERIC(precision=2), nullable=False)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    paid: Mapped[bool] = mapped_column(server_default="False")

    user: Mapped["User"] = relationship(back_populates="fines")
    transaction: Mapped["BookTransaction"] = relationship(back_populates="fine")

    def __repr__(self):
        return f"id: {self.id}, user_id: {self.user_id}, transaction_id: {self.transaction_id}, amount: {self.amount}, date: {self.date}, paid: {self.paid}"

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

    def __repr__(self):
        return f"id: {self.id}, user_id: {self.user_id}, book_id: {self.book_id}, date: {self.date}, due: {self.due}, returned: {self.returned}"