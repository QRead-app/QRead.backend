from datetime import datetime
from zoneinfo import ZoneInfo
from server.model.repository.app_settings_repository import AppSettingsRepository
from server.model.repository.book_repository import BookRepository
from server.model.repository.book_transaction_repository import BookTransactionRepository
from server.model.tables import BookTransaction
from server.util.mailer import mailer

def due_date_reminder(Session) -> None:
    with Session.begin() as session:
        session.expire_on_commit = False
        
        transaction_repo = BookTransactionRepository(session)
        settings_repo = AppSettingsRepository(session)

        transactions = transaction_repo.get_transactions(
            returned = False
        )
        reminder_before_x = settings_repo.get_setting("reminder_x_days_before_due")
        reminder_every_x = settings_repo.get_setting("reminder_every_x_days")

        now = datetime.now(ZoneInfo("Asia/Singapore"))

        for transaction in transactions:
            due_in = transaction.due - now

            if due_in.days == int(reminder_before_x):
                send_reminder(transaction)

            if (
                due_in.days < reminder_before_x 
                and due_in.days % reminder_every_x == 0 
            ):
                send_reminder(transaction)

        def send_reminder(transaction: BookTransaction) -> None:
            book_repo = BookRepository(session)
            book = book_repo.get_book(id = transaction.book_id)
            mailer.send_reminder(book[0], due_in.days)