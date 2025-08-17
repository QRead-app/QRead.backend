import pytest

from flask import current_app, g, session
from tests.test_data import test_admin, test_borrower, test_librarian

### ==========================
### Common - /login
### ==========================

@pytest.mark.parametrize(('email', 'password', 'type', 'error', "code"), (
    (test_admin.email, test_admin.password, "admi", "Invalid path admi", 404),
    (None, test_librarian.password, "librarian", 'Missing email field', 400),
    (test_borrower.email, None, "borrower", 'Missing password field', 400),
    ("emial.com", test_librarian.password, "librarian", 'Invalid email emial.com', 400),
    (test_borrower.email, "randomwrongpassword", "borrower", 'Authentication failed', 401)
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
    (test_librarian.email, test_librarian.password, "librarian", 'Authenticated', 200),
    (test_admin.email, test_admin.password, "admin", 'Authenticated', 200),
    (test_borrower.email, test_borrower.password, "borrower", 'Authenticated', 200),
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
    ("borrower", test_borrower.email, test_borrower.password, "999999", 1),
    ("admin", test_admin.email, test_admin.password, "999999", 1),
    ("librarian", test_librarian.email, test_librarian.password, "999999", 1),
    ("borrower", test_borrower.email, test_borrower.password, None, 2),
    ("admin", test_admin.email, test_admin.password, None, 2),
    ("librarian", test_librarian.email, test_librarian.password, None, 2),
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
            "email": test_librarian.email,
            "password": test_librarian.password
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
        "/book?title=test_title"
    )

    assert response.json.get("message") == "Book(s) retrieved"
    assert response.json.get("data")[0].get("title") == "test_title"
    assert response.status_code == 200

    current_app.config["test_book"] = response.json.get("data")[0]