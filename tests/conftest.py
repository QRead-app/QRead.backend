import pytest

from flask import g 
from server.model.db import DB
from server.model.repository.book_repository import BookRepository
from server.model.repository.book_transaction_repository import BookTransactionRepository
from server.model.repository.fine_repository import FineRepository
from server.model.tables import AccountType
from tests.test_data import *
from server import create_app
from server.model.repository.user_account_repository import UserAccountRepository

@pytest.fixture(scope="session")
def app():
    return create_app()

@pytest.fixture
def client(app):
    return app.test_client()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email: str, password: str, type: AccountType):
        return self._client.post(
            f'/{type.name.lower()}/login',
            json={'email': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(scope="session", autouse=True)
def app_configuration(app, runner):
    with app.app_context():
        runner.invoke(args=["seed-db"])

        db = DB(app.config["TEST_CONNECTION_STRING"])
        Session = db.get_sessionmaker()

        with Session.begin() as session:
            user_repo = UserAccountRepository(session)
            book_repo = BookRepository(session)

            # Insert test users
            user_repo.insert_user(
                name = test_borrower.name,
                email = test_borrower.email,
                password = test_borrower.password,
                type = test_borrower.account_type
            )
            user_repo.insert_user(
                name = test_librarian.name,
                email = test_librarian.email,
                password = test_librarian.password,
                type = test_librarian.account_type
            )
            user_repo.insert_user(
                name = test_admin.name,
                email = test_admin.email,
                password = test_admin.password,
                type = test_admin.account_type
            )

            book_repo.insert_book(
                title = test_book.title,
                description = test_book.description,
                author = test_book.author,
                condition = test_book.condition
            )

        yield app

        with Session.begin() as session:
            user_repo = UserAccountRepository(session)
            book_repo = BookRepository(session)
            fine_repo = FineRepository(session)
            transaction_repo = BookTransactionRepository(session)
            
            # Clean up test users
            user_repo.truncate_table()
            book_repo.truncate_table()
            fine_repo.truncate_table()
            transaction_repo.truncate_table()