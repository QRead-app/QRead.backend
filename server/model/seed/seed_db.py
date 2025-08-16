import click
import random

from decimal import Decimal
from datetime import datetime, timedelta

from server.model.repository.book_return_repository import BookReturnRepository
from server.util.hasher import Hasher
from ..db import DB
from flask import Flask
from .seeds import name, title, description, fine_reason
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
    
    db = DB(app.config["CONNECTION_STRING"])
    Session = db.get_sessionmaker()

    with Session.begin() as session:
        user_account_repo = UserAccountRepository(session)
        book_repo = BookRepository(session)
        transaction_repo = BookTransactionRepository(session)
        fine_repo = FineRepository(session)
        return_repo = BookReturnRepository(session)
        
        print("Truncating all tables...")
        # Truncate all tables
        fine_repo.truncate_table()
        transaction_repo.truncate_table()
        book_repo.truncate_table()
        user_account_repo.truncate_table()
        return_repo.truncate_table()

        # Seed user accounts
        print("Seeding user accounts...")

        names = random.sample(name, 50)
        emails = generate_emails(names)

        for n in range(len(names)):
            type = random.sample(
                [type.value for type in AccountType], counts=[1, 3, 5], k=1)[0]
            user = user_account_repo.insert_user(
                names[n], 
                emails[n], 
                Hasher().hash(names[n].replace(" ", "")), 
                AccountType(type).name,
                AccountState.ACTIVE
            )

            if AccountType(type).name == AccountType.LIBRARIAN.name:
                librarian = user

        user = user_account_repo.insert_user(
            "yen", 
            "looiyen2002@gmail.com", 
            Hasher().hash("yen"), 
            "ADMIN",
            "ACTIVE"
        )

        # Seed books
        print("Seeding books...")

        titles = random.sample(title, 50)
        descriptions = random.sample(description, 50)

        for n in range(len(titles)):
            condition = random.sample(
                [condition.value for condition in BookCondition], k=1)[0]
            author = name[random.randrange(len(name))]
            book_repo.insert_book(
                titles[n], 
                descriptions[n], 
                author, 
                BookCondition(condition).name
            )

        session.flush()

        # Seed book transactions and fines
        print("Seeding transactions, fines & book return...")
        for n in range(50):
            transaction_name = names[random.randrange(len(names))]
            transaction_title = titles[random.randrange(len(titles))]

            transaction_user = user_account_repo.get_user(
                email = generate_email(transaction_name))[0]
            transaction_book = book_repo.get_book(
                title = transaction_title)[0]
            due_date = datetime.now() + timedelta(days=14)

            transaction = transaction_repo.insert_transaction(
                transaction_user.id, transaction_book.id, due_date)
            
            session.flush()

            if (random.randint(1, 3) == 1):
                continue

            amount = random.randint(10, 50) / Decimal(10)
            reason = fine_reason[random.randrange(len(fine_reason))]
            
            fine_repo.insert_fine(
                transaction_user.id, transaction.id, amount, reason)

            return_repo.insert_book_return(
                transaction.id,
                librarian.id
            )

        print("Committing changes...")