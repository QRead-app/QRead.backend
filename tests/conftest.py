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
    client = app.test_client()

    class ClientWrapper:
        def get(self, *args, **kwargs):
            kwargs.setdefault("headers", {})["Origin"] = "http://other-site.com"
            return client.get(*args, **kwargs)

        def post(self, *args, **kwargs):
            kwargs.setdefault("headers", {})["Origin"] = "http://other-site.com"
            return client.post(*args, **kwargs)

    return ClientWrapper()

@pytest.fixture
def client_factory(app):
    def _get_client(type: str):
        if type == "borrower":
            email = borrower.email
            password = borrower.password
        elif type == "admin":
            email = admin.email
            password = admin.password
        elif type == "librarian":
            email = librarian.email
            password = librarian.password
        elif type == "borrower2":
            email = borrower_2.email
            password = borrower_2.password
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
            def insert_user(user: User):
                if user.account_state is None:
                    user.account_state = AccountState.ACTIVE

                user_repo.insert_user(
                    name = user.name,
                    email = user.email,
                    password = hasher.hash(user.password),
                    type = user.account_type,
                    state = user.account_state
                )

            insert_user(borrower)
            insert_user(borrower_deleted)
            insert_user(borrower_suspended)
            insert_user(borrower_2)
            insert_user(admin)
            insert_user(admin_suspended)
            insert_user(admin_deleted)
            insert_user(librarian)
            insert_user(librarian_suspended)
            insert_user(librarian_deleted)
            
            book_repo.insert_book(
                title = book.title,
                description = book.description,
                author = book.author,
                condition = book.condition
            )

        yield app

        with Session.begin() as session:
            runner.invoke(args=["seed-db"])