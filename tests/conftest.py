import pytest

from flask import current_app, g 
from server.model.db import DB
from server.model.repository.book_repository import BookRepository
from server.util.extensions import otp_cache, mailer
from server.util.hasher import Hasher
from tests.test_data import *
from server import create_app
from server.model.repository.user_account_repository import UserAccountRepository

@pytest.fixture(scope="session")
def app():
    return create_app("testing")

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def client_factory(app):
    def _get_client(type: str):
        if type == "borrower":
            email = test_borrower.email
            password = test_borrower.password
        elif type == "admin":
            email = test_admin.email
            password = test_admin.password
        elif type == "librarian":
            email = test_librarian.email
            password = test_librarian.password
        elif type == "borrower2":
            email = test_borrower_2.email
            password = test_borrower_2.password
            type = "borrower"
        else:
            raise Exception("Invalid client type")

        client = app.test_client()

        with mailer.record_messages() as outbox:
            client.post(
                f"/{type}/login",
                json = {
                    "email": email,
                    "password": password
                }
            )
            otp = outbox[0].body[-6:]
        
        client.post(
            "/verify-otp",
            json = {
                "otp": otp
            }
        )
        
        return client
    return _get_client

@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(scope="session", autouse=True)
def app_configuration(app, runner):
    with app.app_context():
        db = DB.get_db()
        Session = db.get_sessionmaker()
        runner.invoke(args=["seed-db"])

        with Session.begin() as session:
            user_repo = UserAccountRepository(session)
            book_repo = BookRepository(session)
            hasher = Hasher()

            # Insert test users
            user_repo.insert_user(
                name = test_borrower.name,
                email = test_borrower.email,
                password = hasher.hash(test_borrower.password),
                type = test_borrower.account_type
            )
            user_repo.insert_user(
                name = test_borrower_2.name,
                email = test_borrower_2.email,
                password = hasher.hash(test_borrower_2.password),
                type = test_borrower_2.account_type
            )
            user_repo.insert_user(
                name = test_librarian.name,
                email = test_librarian.email,
                password = hasher.hash(test_librarian.password),
                type = test_librarian.account_type
            )
            user_repo.insert_user(
                name = test_admin.name,
                email = test_admin.email,
                password = hasher.hash(test_admin.password),
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
            runner.invoke(args=["seed-db"])