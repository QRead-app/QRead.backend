import click
import random

from decimal import Decimal
from datetime import datetime, timedelta

from server.model.repository.app_settings_repository import AppSettingsRepository
from server.model.repository.book_return_repository import BookReturnRepository
from server.util.hasher import Hasher
from ..db import DB
from flask import Flask
from .seeds import name, title, description, fine_reason, images
from ..tables import *
from ..repository.user_account_repository import UserAccountRepository
from ..repository.book_repository import BookRepository
from ..repository.book_transaction_repository import BookTransactionRepository
from ..repository.fine_repository import FineRepository
from ..tables import AccountType, BookCondition

def init_app(app: Flask):
    app.cli.add_command(seed_db_command)

def generate_emails(names: list[str]) -> list[str]:
    return [f"{name.replace(' ', '')}@email.com" for name in names]

def generate_email(name: str) -> str:
    return f"{name.replace(' ', '')}@email.com"

@click.command("seed-db")
def seed_db_command():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=False)

    if app.config["ENVIRONMENT"] == 'testing':
        app.config.from_object('server.config.TestingConfig')
        app.config["CONNECTION_STRING"] = app.config["TEST_CONNECTION_STRING"]
    
    db = DB()
    Session = db.get_sessionmaker()

    with Session.begin() as session:
        user_account_repo = UserAccountRepository(session)
        book_repo = BookRepository(session)
        transaction_repo = BookTransactionRepository(session)
        fine_repo = FineRepository(session)
        return_repo = BookReturnRepository(session)
        settings_repo = AppSettingsRepository(session)
        
        print("Truncating all tables...")
        # Truncate all tables
        fine_repo.truncate_table()
        transaction_repo.truncate_table()
        book_repo.truncate_table()
        user_account_repo.truncate_table()
        return_repo.truncate_table()
        settings_repo.truncate_table()

        print("Seeding app settings...")
        settings_repo.insert_setting("reminder_x_days_before_due", "7")
        settings_repo.insert_setting("reminder_every_x_days", "1")

        # Seed user accounts
        print("Seeding user accounts...")

        names = random.sample(name, 50)
        emails = generate_emails(names)

        users = {
            "ADMIN": {
                "ACTIVE": [],
                "SUSPENDED": [],
                "DELETED": []
            },
            "LIBRARIAN": {
                "ACTIVE": [],
                "SUSPENDED": [],
                "DELETED": []
            },
            "BORROWER": {
                "ACTIVE": [],
                "SUSPENDED": [],
                "DELETED": []
            },
        }
        
        def create_user(name: str, email: str, type: AccountType, state: AccountState):
            user = user_account_repo.insert_user(
                name, 
                email, 
                Hasher().hash(name.replace(" ", "")), 
                type,
                state
            )

            users[user.account_type.name][user.account_state.name].append(user)

        user_no = 0 
        create_user(names[user_no], emails[user_no], AccountType.ADMIN, AccountState.ACTIVE)
        user_no += 1
        create_user(names[user_no], emails[user_no], AccountType.ADMIN, AccountState.SUSPENDED)
        user_no += 1
        create_user(names[user_no], emails[user_no], AccountType.ADMIN, AccountState.DELETED)
        user_no += 1

        create_user(names[user_no], emails[user_no], AccountType.LIBRARIAN, AccountState.ACTIVE)
        user_no += 1
        create_user(names[user_no], emails[user_no], AccountType.LIBRARIAN, AccountState.SUSPENDED)
        user_no += 1
        create_user(names[user_no], emails[user_no], AccountType.LIBRARIAN, AccountState.DELETED)
        user_no += 1

        create_user(names[user_no], emails[user_no], AccountType.BORROWER, AccountState.SUSPENDED)
        user_no += 1
        create_user(names[user_no], emails[user_no], AccountType.BORROWER, AccountState.DELETED)
        user_no += 1

        [create_user(names[no], emails[no], AccountType.BORROWER, AccountState.ACTIVE) for no in range(user_no, 50)]

        user_account_repo.insert_user(
            "yen", 
            "looiyen2002@gmail.com", 
            Hasher().hash("yen"), 
            "ADMIN",
            "ACTIVE"
        )

        user_account_repo.insert_user(
            "hyeri", 
            "daramggi136@gmail.com", 
            Hasher().hash("123456"), 
            "ADMIN",
            "ACTIVE"
        )

        user_account_repo.insert_user(
            "aziz", 
            "azxz1603@gmail.com", 
            Hasher().hash("123456"), 
            "LIBRARIAN",
            "ACTIVE"
        )

        user_account_repo.insert_user(
            "borrower", 
            "borrower@gmail.com", 
            Hasher().hash("borrower"), 
            "BORROWER",
            "ACTIVE"
        )

        user_account_repo.insert_user(
            "admin", 
            "admin@gmail.com", 
            Hasher().hash("admin"), 
            "ADMIN",
            "ACTIVE"
        )

        user_account_repo.insert_user(
            "librarian", 
            "librarian@gmail.com", 
            Hasher().hash("librarian"), 
            "LIBRARIAN",
            "ACTIVE"
        )

        # Seed books
        print("Seeding books...")

        titles = random.sample(title, 50)
        descriptions = random.sample(description, 50)
        books = []
        for n in range(len(titles)):
            condition = random.sample(
                [condition.value for condition in BookCondition], k=1)[0]
            author = name[random.randrange(len(name))]
            book = book_repo.insert_book(
                titles[n], 
                descriptions[n], 
                author, 
                BookCondition(condition).name,
                image=random.choice(images)
            )
            books.append(book)

        session.flush()

        book_repo.insert_book(
            'Finding Audrey', 
            'From the #1 New York Times bestselling author of the Shopaholic series comes a terrific blend of comedy, romance, and psychological recovery in a contemporary YA novel sure to inspire and entertain. An anxiety disorder disrupts fourteen-year-old Audrey\'s daily life...', 
            'Sophie Kinsella', 
            BookCondition.VERY_GOOD,
            image=random.choice(images)
        )

        # Seed book transactions and fines
        print("Seeding transactions, fines & book return...")
        
        def book_manage(book: Book):
            librarian = user_account_repo.get_user(
                account_type=AccountType.LIBRARIAN,
                account_state = AccountState.ACTIVE
            )
            transaction_user = user_account_repo.get_user(
                account_type=AccountType.BORROWER
            )
            transaction_user = random.choice(transaction_user)
            
            # 20% overdue
            due = False
            if (random.randint(1, 5) == 1):
                due = True
                due_date = datetime.now() - timedelta(days=2)
            else: 
                due_date = datetime.now() + timedelta(days=14)

            transaction = transaction_repo.insert_transaction(
                transaction_user.id, book.id, due_date)
            book = book_repo.get_book(id=book.id)[0]
            
            session.flush()

            book.on_loan = True
            if due:
                book.on_loan = False
                transaction.returned = True
                return_repo.insert_book_return(transaction.id, random.choice(librarian).id)

                amount = random.randint(10, 50) / Decimal(10)
                fine_repo.insert_fine(
                    transaction_user.id, transaction.id, amount, "Overdue")
                return book_manage(book)

            # 24% Not returned and not overdue
            if (random.randint(1, 3) == 1):
                return

            # 52% Returned or fined  
            if (random.randint(1, 2) == 1):
                book.on_loan = False
                transaction.returned = True
                return_repo.insert_book_return(transaction.id, random.choice(librarian).id)
            
                amount = random.randint(10, 50) / Decimal(10)
                reason = fine_reason[random.randrange(len(fine_reason))]
                
                fine_repo.insert_fine(
                    transaction_user.id, transaction.id, amount, reason)
                return book_manage(book)

            librarian = random.choice(librarian)  
            return_repo.insert_book_return(
                transaction.id,
                librarian.id
            )
            book.on_loan = False

            transaction.returned = True
            if (random.randint(1, 3) == 1):
                return

            book_manage(book)
        
        for book in books:
            book_manage(book)

        print("Committing changes...")