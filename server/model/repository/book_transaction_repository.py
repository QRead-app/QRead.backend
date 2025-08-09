from datetime import datetime
from ..tables import BookTransaction
from .base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session

class BookTransactionRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_transactions(
        self, 
        id: int | None = None, 
        user_id: int | None = None, 
        book_id: int | None = None, 
        date: datetime | None = None, 
        due: datetime | None = None, 
        returned: bool | None = None
    ) -> list[BookTransaction] | None:
        stmt = select(BookTransaction)

        filters = []
        if id is not None:
            filters.append(BookTransaction.id == id)
        if user_id is not None:
            filters.append(BookTransaction.user_id == user_id)
        if book_id is not None:
            filters.append(BookTransaction.book_id == book_id)
        if date is not None:
            filters.append(BookTransaction.date == date)
        if due is not None:
            filters.append(BookTransaction.due == due)
        if returned is not None:
            filters.append(BookTransaction.returned == returned)

        if filters: 
            stmt = stmt.where(*filters)

        return self.session.execute(stmt).scalars().all()

    def insert_transaction(
        self, 
        user_id: int, 
        book_id: int, 
        due_date: datetime
    ) -> BookTransaction:
        transaction = BookTransaction(user_id = user_id, book_id = book_id, due = due_date)
        self.session.add(transaction)

        return transaction