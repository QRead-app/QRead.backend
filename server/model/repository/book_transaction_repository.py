from datetime import datetime
from ..tables import BookTransaction
from .base_repository import BaseRepository
from sqlalchemy import Row, select
from sqlalchemy.orm import Session

class BookTransactionRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_transaction_by_id(self, id: int) -> BookTransaction|None:
        return self.session.get(BookTransaction, id)
    
    def get_transactions_by_user_id(self, id: int) -> Row[BookTransaction]|None:
        return self.session.execute(
            select(BookTransaction)
                .where(BookTransaction.user_id == id)
        ).all()
    
    def get_transactions_by_book_id(self, id: str) -> Row[BookTransaction]|None:
        return self.session.execute(
            select(BookTransaction)
                .where(BookTransaction.book_id == id)
        ).all()

    def insert_transaction(self, user_id: int, book_id: int, due_date: datetime) -> BookTransaction:
        transaction = BookTransaction(user_id = user_id, book_id = book_id, due = due_date)
        self.session.add(transaction)

        return transaction