import pytest

from tests.test_users import test_admin, test_borrower, test_librarian


@pytest.mark.parametrize(('email', 'password', 'type', 'message', "code"), (
    ('', '', "admi", "Invalid path admi", 404),
    ('', 'a', "admin", 'Authentication failed', 401),
    ('a', '', "borrower", 'Authentication failed', 401),
    ('', '', "librarian", 'Authentication failed', 401),
    (test_borrower.email, '', "borrower", 'Authentication failed', 401),
    ('', test_librarian.password, "librarian", 'Authentication failed', 401),
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