import decimal

from ..tables import Fine
from .base_repository import BaseRepository
from sqlalchemy import Row, select
from sqlalchemy.orm import Session

class FineRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_fine_by_id(self, id: int) -> Fine|None:
        return self.session.get(Fine, id)
    
    def get_fines_by_user_id(self, id: int) -> Row[Fine]|None:
        return self.session.execute(
            select(Fine)
                .where(Fine.user_id == id)
        ).all()
    
    def get_transactions_by_transaction_id(self, id: str) -> Row[Fine]|None:
        return self.session.execute(
            select(Fine)
                .where(Fine.transaction_id == id)
        ).all()

    def insert_fine(self, user_id: int, transaction_id: int, amount: decimal.Decimal) -> Fine:
        fine = Fine(user_id = user_id, transaction_id = transaction_id, amount = amount)
        self.session.add(fine)
        
        return fine