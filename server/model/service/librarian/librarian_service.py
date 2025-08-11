from decimal import Decimal
from server.model.repository.fine_repository import FineRepository
from server.model.service.base_service import BaseService
from server.model.service.transactional_wrapper import transactional
from server.model.tables import Fine

class LibrarianService(BaseService):
    def __init__(self, Session):
        super().__init__(Session)

    @transactional
    def issue_fine(self, user_id: int, transaction_id: int, amount: Decimal, reason: str) -> Fine:
        fine_repo = FineRepository(self.session)

        fine = fine_repo.insert_fine(user_id, transaction_id, amount, reason)

        return fine