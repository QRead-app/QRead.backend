import pytest

from flask import current_app, g, session
from tests.test_data import *
from server.util.extensions import mailer as mail

### ==========================
### Common - /login
### ==========================

@pytest.mark.parametrize(('email', 'password', 'type', 'error', "code"), (
    (admin.email, admin.password, "admi", "Invalid path admi", 404),
    (None, librarian.password, "librarian", 'Missing email field', 400),
    (borrower.email, None, "borrower", 'Missing password field', 400),
    ("emial.com", librarian.password, "librarian", 'Invalid email emial.com', 400),
    (borrower.email, "randomwrongpassword", "borrower", 'Authentication failed', 401),
    (admin_suspended.email, admin_suspended.password, "admin", "User has been Suspended", 400),
    (librarian_suspended.email, librarian_suspended.password, "librarian", "User has been Suspended", 400),
    (borrower_suspended.email, borrower_suspended.password, "borrower", "User has been Suspended", 400),
    (admin_deleted.email, admin_deleted.password, "admin", "User has been Deleted", 400),
    (librarian_deleted.email, librarian_deleted.password, "librarian", "User has been Deleted", 400),
    (borrower_deleted.email, borrower_deleted.password, "borrower", "User has been Deleted", 400)
))
def test_log_in_bad(client, email, password, type, error, code):
    response = client.post(
        f"/{type}/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.json.get("error") == error
    assert response.status_code == code

@pytest.mark.parametrize(('email', 'password', 'type', 'message', "code"), (
    (librarian.email, librarian.password, "librarian", 'Authenticated', 200),
    (admin.email, admin.password, "admin", 'Authenticated', 200),
    (borrower.email, borrower.password, "borrower", 'Authenticated', 200),
))
def test_log_in_good(client, email, password, type, message, code):
    response = client.post(
        f"/{type}/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.json.get("message") == message
    assert response.status_code == code

### ==========================
### Common - /verify-otp
### ==========================

def test_verify_otp_bad_havent_login(client):
    response = client.post(
        "/verify-otp",
        json = {}
    )

    assert response.json.get("error") == "Not authenticated"
    assert response.status_code == 401

@pytest.mark.parametrize(('type', "email", "password", "otp", "scenario"), (
    ("borrower", borrower.email, borrower.password, "999999", 1),
    ("admin", admin.email, admin.password, "999999", 1),
    ("librarian", librarian.email, librarian.password, "999999", 1),
    ("borrower", borrower.email, borrower.password, None, 2),
    ("admin", admin.email, admin.password, None, 2),
    ("librarian", librarian.email, librarian.password, None, 2),
))
def test_verify_otp_bad_after_login(client, type, email, password, otp, scenario):
    client.post(
        f"/{type}/login",
        json = {
            "email": email,
            "password": password
        }
    )

    response = client.post(
        "/verify-otp",
        json = {
            "otp": otp
        }
    )

    if scenario == 1:
        assert response.json.get("error") == "Wrong OTP"
        assert response.status_code == 401
    if scenario == 2:
        assert response.json.get("error") == "Missing otp field"
        assert response.status_code == 400

@pytest.mark.parametrize(('type'), (
    ("borrower"),
    ("admin"),
    ("librarian"),
))
def test_verify_otp_good(client_factory, type):
    client_factory(type)

### ==========================
### Common - /logout
### ==========================

def test_log_out_good_without_session(client):
    response = client.post("/logout")

    assert response.json.get("message") == "No active session"
    assert response.status_code == 200

@pytest.mark.parametrize(('type'), (
    ("borrower"),
    ("admin"),
    ("librarian"),
))
def test_log_out_good_with_session(client_factory, type):
    client = client_factory(type)
    client.post(
        "/librarian/login",
        json = {
            "email": librarian.email,
            "password": librarian.password
        }
    )

    response = client.post(
        "/logout"
    )

    assert response.json.get("message") == "Logout successful"
    assert response.status_code == 200

### ==========================
### Common - /book
### ==========================

@pytest.mark.parametrize(("id", "title", "condition", "message", "code"), (
    ("12", "random wrong title", "FAIR", "No book found", 200),
    ("HI", "random wrong title", "FAIR", "Invalid book id HI", 400),
    ("12", "random wrong title", "PRISTINE", "Invalid book condition PRISTINE", 400),
))
def test_get_book_bad(client, id, title, condition, message, code):
    response = client.get(
        f"/book?id={id}&title={title}&condition={condition}"
    )

    assert ( 
        response.json.get("message") == message
        or response.json.get("error") == message
    )
    assert response.status_code == code

def test_get_book_good(client):
    response = client.get(
        "/book?title=title"
    )

    assert response.json.get("message") == "Book(s) retrieved"
    assert response.json.get("data")[0].get("title") == "title"
    assert response.status_code == 200

    current_app.config["book"] = response.json.get("data")[0]

### ==========================
### Common - /forgot-password
### ==========================

@pytest.mark.parametrize(("email", "redirect", "error", "code"), (
    ("wrong_email@eee.com", "redirect", "Email not found", 404),
    ("wrong_email", "redirect", "Invalid email wrong_email", 400),
    (None, "redirect", "Missing email field", 400),
    (borrower.email, None, "Missing redirect field", 400)
))
def test_forgot_password_bad(client, email, redirect, error, code):
    response = client.post(
        f"/forgot-password",
        json = {
            "email": email,
            "redirect": redirect
        }
    )

    assert response.json.get("error") == error
    assert response.status_code == code

def test_forgot_password_and_reset_password_good(client):
    with mail.record_messages() as outbox:
        response = client.post(
            "/forgot-password",
            json = {
                "email": borrower.email,
                "redirect": "test"
            }
        )

        assert response.json.get("message") == "Reset password email sent"
        assert response.status_code == 200

        secret = outbox[0].body.split("secret=")[1]

        response = client.post(
            "/reset-password",
            json = {
                "secret": secret,
                "password": "123123"
            }
        )

        assert response.json.get("message") == "Password successfully updated"
        assert response.status_code == 200

        response = client.post(
            f"/borrower/login",
            json={
                "email": borrower.email,
                "password": "123123"
            }
        )

        assert response.json.get("message") == "Authenticated"
        assert response.status_code == 200

        response = client.post(
            "/forgot-password",
            json = {
                "email": borrower.email,
                "redirect": "test"
            }
        )
        secret = outbox[0].body.split("secret=")[1]

        response = client.post(
            "/reset-password",
            json = {
                "secret": secret,
                "password": borrower.password
            }
        )
        
def test_reset_password_bad_wrong_secret(client):
    with mail.record_messages() as outbox:
        response = client.post(
            "/forgot-password",
            json = {
                "email": borrower.email,
                "redirect": "test"
            }
        )

        assert response.json.get("message") == "Reset password email sent"
        assert response.status_code == 200

        response = client.post(
            "/reset-password",
            json = {
                "secret": "123",
                "password": "123123"
            }
        )

        assert response.json.get("error") == "Wrong secret 123"
        assert response.status_code == 401

def test_reset_password_bad_missing_secret(client):
    with mail.record_messages() as outbox:
        response = client.post(
            "/forgot-password",
            json = {
                "email": borrower.email,
                "redirect": "test"
            }
        )

        assert response.json.get("message") == "Reset password email sent"
        assert response.status_code == 200

        response = client.post(
            "/reset-password",
            json = {
                "password": "123123"
            }
        )

        assert response.json.get("error") == "Missing secret field"
        assert response.status_code == 400

def test_reset_password_bad_missing_password(client):
    with mail.record_messages() as outbox:
        response = client.post(
            "/forgot-password",
            json = {
                "email": borrower.email,
                "redirect": "test"
            }
        )
        secret = outbox[0].body.split("secret=")[1]

        assert response.json.get("message") == "Reset password email sent"
        assert response.status_code == 200

        response = client.post(
            "/reset-password",
            json = {
                "secret": secret,
            }
        )

        assert response.json.get("error") == "Missing password field"
        assert response.status_code == 400