import pytest

from tests.test_users import test_admin, test_borrower, test_librarian


@pytest.mark.parametrize(('name', 'email', 'password', 'message', "code"), (
    (None, None, None, "Missing fields", 400),
    (None, 'testtest@test.com', "admin", 'Missing fields', 400),
    ('test123', None, "test123", 'Missing fields', 400),
    (None, None, "test123", 'Missing fields', 400),
    (test_borrower.name, test_borrower.email, "borrower", 'The email provided is already registered', 400),
    ("Emailemail.com", "Emailemail.com", "librarian", 'Invalid Email', 400)
))
def test_register_bad(client, name, email, password, message, code):
    response = client.post(
        f"/borrower/register",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )

    assert response.json.get("error") == message
    assert response.status_code == code

def test_register_good(client):
    response = client.post(
        f"/borrower/register",
        json={
            "name": "TestUSER123",
            "email": "TestUSER123@email.com",
            "password": "TestUSER123"
        }
    )

    assert response.json.get("message") == "Registered"
    assert response.status_code == 200

