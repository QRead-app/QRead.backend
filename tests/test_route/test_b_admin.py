import pytest

from flask import current_app, g, session
from tests.test_data import *
from server.util.extensions import mailer as mail
from tests.extensions import test_cache

### ==========================
### Admin - /register-librarian
### ==========================

@pytest.mark.parametrize(('email', 'redirect', 'error', "code"), (
    (None, "test", "Missing email field", 400),
    ("test123@me.com", None, "Missing redirect field", 400),
    ("test", "tesT", "Invalid email test", 400),
    (admin.email, 'test', f"Email {admin.email} is already registered", 400),
    (borrower.email, 'test', f"Email {borrower.email} is already registered", 400),
    (librarian.email, 'test', f"Email {librarian.email} is already registered", 400),
))
def test_register_librarian_bad(client_factory, email, redirect, error, code):
    client = client_factory("admin")

    response = client.post(
        f"/admin/register-librarian",
        json={
            "email": email,
            "redirect": redirect
        }
    )

    assert response.json.get("error") == error
    assert response.status_code == code

def test_register_librarian_good(client_factory):
    client = client_factory("admin")

    with mail.record_messages() as outbox:
        response = client.post(
            "/admin/register-librarian",
            json = {
                "email": "testtest@email.com",
                "redirect": "test"
            }
        )

        assert response.json.get("message") == "Invitation email sent"
        assert response.status_code == 200

        secret = outbox[0].body.split("secret=")[1]
        response = client.post(
            "/new-librarian",
            json = {
                "secret": secret,
                "name": "new_lib",
                "password": "123123"
            }
        )

        assert response.json.get("message") == "Librarian created successfully"
        assert response.status_code == 200

        response = client.post(
            f"/librarian/login",
            json={
                "email": "testtest@email.com",
                "password": "123123"
            }
        )

        assert response.json.get("message") == "Authenticated"
        assert response.status_code == 200

def test_new_librarian_bad_missing_secret(client_factory):
    client = client_factory("admin")

    with mail.record_messages() as outbox:
        response = client.post(
            "/admin/register-librarian",
            json = {
                "email": "testtes1@email.com",
                "redirect": "test"
            }
        )
        secret = outbox[0].body.split("secret=")[1]

        assert response.json.get("message") == "Invitation email sent"
        assert response.status_code == 200

        response = client.post(
            "/new-librarian",
            json = {
                "name": "new_lib",
                "password": "123123"
            }
        )

        assert response.json.get("error") == "Missing secret field"
        assert response.status_code == 400

def test_new_librarian_bad_missing_name(client_factory):
    client = client_factory("admin")

    with mail.record_messages() as outbox:
        response = client.post(
            "/admin/register-librarian",
            json = {
                "email": "testtest1@email.com",
                "redirect": "test"
            }
        )
        secret = outbox[0].body.split("secret=")[1]

        assert response.json.get("message") == "Invitation email sent"
        assert response.status_code == 200

        response = client.post(
            "/new-librarian",
            json = {
                "secret": secret,
                "password": "123123"
            }
        )

        assert response.json.get("error") == "Missing name field"
        assert response.status_code == 400

def test_new_librarian_bad_missing_password(client_factory):
    client = client_factory("admin")

    with mail.record_messages() as outbox:
        response = client.post(
            "/admin/register-librarian",
            json = {
                "email": "testtest1@email.com",
                "redirect": "test"
            }
        )
        secret = outbox[0].body.split("secret=")[1]

        assert response.json.get("message") == "Invitation email sent"
        assert response.status_code == 200

        response = client.post(
            "/new-librarian",
            json = {
                "secret": secret,
                "name": "test"
            }
        )

        assert response.json.get("error") == "Missing password field"
        assert response.status_code == 400

def test_new_librarian_bad_wrong_secret(client_factory):
    client = client_factory("admin")

    with mail.record_messages() as outbox:
        response = client.post(
            "/admin/register-librarian",
            json = {
                "email": "testtest1@email.com",
                "redirect": "test"
            }
        )
        secret = outbox[0].body.split("secret=")[1]

        assert response.json.get("message") == "Invitation email sent"
        assert response.status_code == 200

        response = client.post(
            "/new-librarian",
            json = {
                "secret": "123123",
                "name": "test",
                "password": "123123"
            }
        )

        assert response.json.get("error") == "Wrong secret 123123"
        assert response.status_code == 401

### ==========================
### Admin - GET /users
### ==========================

@pytest.mark.parametrize(
    ('email', 'type'), (
        (borrower.email, 'borrower'),
        (admin.email, 'admin'),
        (librarian.email, 'librarian')
    )
)
def test_get_user_by_email_good(client_factory, email, type):
    client = client_factory("admin")

    response = client.get(
        f"/admin/users?email={email}",
    )

    assert "data" in response.json
    assert response.status_code == 200
    
    data = response.json.get("data")[0]
    assert "user" in data
    assert "transaction" in data
    assert "fine" in data
    
    test_cache.set(f"{type}_id", response.json.get("data")[0].get("user").get("id"))

@pytest.mark.parametrize(
    ('type'), (
        ('borrower'),
        ('admin'),
        ('librarian')
    )
)
def test_get_user_by_id_good(client_factory, type):
    client = client_factory("admin")

    response = client.get(
        f"/admin/users?id={test_cache.get(f'{type}_id')}",
    )

    assert "data" in response.json
    assert response.status_code == 200
    
    data = response.json.get("data")[0]
    assert "user" in data
    assert "transaction" in data
    assert "fine" in data


    assert data.get("user").get("account_type").lower() == type

### ==========================
### Admin - PUT /user
### ==========================

### ==========================
### Admin - DELETE /user
### ==========================

### ==========================
### Admin - /suspend-user
### ==========================

### ==========================
### Admin - /reinstate-user
### ==========================

### ==========================
### Admin - GET /app-setting
### ==========================

### ==========================
### Admin - PUT /app-setting
### ==========================
