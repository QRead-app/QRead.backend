from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app

from server.model.db import DB
from server.model.repository.app_settings_repository import AppSettingsRepository
from server.model.repository.book_repository import BookRepository
from server.model.repository.book_transaction_repository import BookTransactionRepository
from server.model.repository.user_account_repository import UserAccountRepository
from server.model.tables import BookTransaction
from server.util.mailer import mailer

def due_date_reminder() -> None:
    with current_app.app_context():
        db = DB.get_db()
        Session = db.get_sessionmaker()

        with Session.begin() as session:
            session.expire_on_commit = False
            
            transaction_repo = BookTransactionRepository(session)
            settings_repo = AppSettingsRepository(session)

            transactions = transaction_repo.get_transactions(
                returned = False
            )
            reminder_before_x = int(settings_repo.get_setting("reminder_x_days_before_due").value)
            reminder_every_x = int(settings_repo.get_setting("reminder_every_x_days").value)

            now = datetime.now()

            def send_reminder(transaction: BookTransaction) -> None:
                user_repo = UserAccountRepository(session)
                book_repo = BookRepository(session)

                book = book_repo.get_book(id = transaction.book_id)
                user = user_repo.get_user(id = transaction.user_id)
                mailer.send_reminder(user[0].email, book[0], due_in.days)

            for transaction in transactions:
                due_in = transaction.due - now

                if due_in.days == int(reminder_before_x):
                    send_reminder(transaction)

                if (
                    due_in.days < reminder_before_x 
                    and due_in.days % reminder_every_x == 0 
                ):
                    send_reminder(transaction)