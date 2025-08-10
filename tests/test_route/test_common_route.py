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

    if "message" in response.json:
        assert response.json["message"]
    else:
        assert response.json["error"]
    assert response.status_code == code