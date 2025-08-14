import pytest

from flask import current_app, g
from tests.test_data import test_admin, test_borrower, test_librarian


@pytest.mark.parametrize(('email', 'password', 'type', 'message', "code"), (
    ('', '', "admi", "Invalid path admi", 404),
    (None, "a", "librarian", 'Missing email field', 400),
    ("a", None, "librarian", 'Missing password field', 400),
    ("emial.com", test_librarian.password, "librarian", 'Invalid email emial.com', 400),
    (test_borrower.email, '', "borrower", 'Authentication failed', 401),
    (test_librarian.email, test_librarian.password, "librarian", 'Login successful', 200),
))
def test_log_in(client, email, password, type, message, code):
    response = client.post(
        f"/{type}/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert ( 
        response.json.get("message") == message
        or response.json.get("error") == message
    )
    assert response.status_code == code

def test_log_out_without_session(client):
    response = client.post("/logout")

    assert response.json.get("message") == "No active session"
    assert response.status_code == 200

def test_log_out_with_session(client):
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