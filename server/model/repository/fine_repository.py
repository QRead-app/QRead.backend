from datetime import datetime
import decimal

from ..tables import Fine
from .base_repository import BaseRepository
from sqlalchemy import select, text
from sqlalchemy.orm import Session

class FineRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_fine(
        self, 
        id: int | None = None, 
        user_id: int | None = None, 
        transaction_id: int | None = None, 
        amount: decimal.Decimal | None = None, 
        reason: str | None = None,
        date: datetime | None = None, 
        paid: bool | None = None
    ) -> list[Fine] | None:
        stmt = select(Fine)

        filters = []
        if id is not None:
            filters.append(Fine.id == id)
        if user_id is not None:
            filters.append(Fine.user_id == user_id)
        if transaction_id is not None:
            filters.append(Fine.transaction_id == transaction_id)
        if amount is not None:
            filters.append(Fine.amount == amount)
        if reason is not None:
            filters.append(Fine.reason == reason)
        if date is not None:
            filters.append(Fine.date == date)
        if paid is not None:
            filters.append(Fine.paid == paid)

        if filters: 
            stmt = stmt.where(*filters)

        return self.session.execute(stmt).scalars().all()

    def insert_fine(
        self, 
        user_id: int, 
        transaction_id: int,
        amount: decimal.Decimal,
        reason: str,
    ) -> Fine:
        fine = Fine(
            user_id = user_id, 
            transaction_id = transaction_id, 
            reason = reason,
            amount = amount
        )
        self.session.add(fine)
        
        return fine
    
    def truncate_table(self) -> None:
        self.session.execute(text("TRUNCATE TABLE fine CASCADE"))