import pytest

from flask import g
from server.model.tables import AccountType
from tests.test_users import test_borrower, test_librarian, test_admin
from server import create_app
from server.model.repository.user_account_repository import UserAccountRepository

@pytest.fixture
def app():
    app = create_app()

    with app.app_context():
        user_repo = UserAccountRepository(g.Session)

        # Insert test users
        g.borrower = user_repo.insert_user(
            name = test_borrower.name,
            email = test_borrower.email,
            password = test_borrower.password,
            type = test_borrower.account_type
        )
        g.librarian = user_repo.insert_user(
            name = test_librarian.name,
            email = test_librarian.email,
            password = test_librarian.password,
            type = test_librarian.account_type
        )
        g.admin = user_repo.insert_user(
            name = test_admin.name,
            email = test_admin.email,
            password = test_admin.password,
            type = test_admin.account_type
        )

        yield app

        # Clean up test users
        user_repo.delete_user(g.borrower)
        user_repo.delete_user(g.librarian)
        user_repo.delete_user(g.admin)


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