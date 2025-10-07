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

@pytest.mark.parametrize(
    ("id", "name", "email", "state", "password", "newpassword", "error", "status_code"), (
        ("test", "test2", None, None, None, None, "Invalid id test", 400),
        (123123123, "test2", None, None, None, None, "User not found", 404),
        ("borrower", None, "test", None, None, None, "Invalid email test", 400),
        ("borrower", None, None, "TEST", None, None, "Invalid account_state TEST", 400),
        (None, None, None, None, "testwrongpass121", "newpass", "Old password is wrong", 400)
    )
)
def test_update_user_bad(client_factory, id, name, email, state, password, newpassword, error, status_code):
    client = client_factory("admin")

    if id == "borrower":
        id = test_cache.get("borrower_id")

    url = ''
    if id is not None: url = url + f'id={id}&'
    if name is not None: url = url + f'name={name}&'
    if email is not None: url = url + f'email={email}&'
    if state is not None: url = url + f'state={state}&'
    if password is not None: url = url + f'password={password}&'
    if newpassword is not None: url = url + f'&newpassword={newpassword}'

    response = client.put(
        f"""/admin/user?{url}"""
    )

    assert response.json.get("error") == error
    assert response.status_code == status_code

def test_update_user_details_good(client_factory):
    client = client_factory("admin")

    id = test_cache.get("borrower_2_id")

    response = client.put(
        f"""/admin/user?id={id}&name=testtest_borrower&email=test_borrower_2@email.com&state=DELETED"""
    )

    assert response.json.get("message") == "User updated"
    assert response.status_code == 200

    response = client.get(
        f"/admin/users?id={id}",
    )

    user = response.json.get("data")[0].get("user")
    assert user.get("name") == "testtest_borrower"
    assert user.get("email") == "test_borrower_2@email.com"
    assert user.get("account_state") == "DELETED"

    client.put(
        f"""/admin/user?id={id}&name={borrower_2.name}&email={borrower_2.email}&state={borrower_2.account_state}"""
    )


### ==========================
### Admin - DELETE /user
### ==========================

@pytest.mark.parametrize(
    ("id", "error", "status_code"), (
        (None, "Missing id field", 400),
        (12312312, "User id 12312312 not found", 404),
        ('abc', "Invalid id abc", 400)
    )
)
def test_delete_user_bad(client_factory, id, error, status_code):
    client = client_factory("admin")

    if id is not None: url = f'id={id}'
    else: url = ''

    response = client.delete(
        f"""/admin/user?{url}"""
    )

    assert response.json.get("error") == error
    assert response.status_code == status_code

def test_delete_user_good(client_factory):
    client = client_factory('admin')

    response = client.delete(
        f'/admin/user?id={test_cache.get("borrower_2_id")}'
    )

    assert response.json.get('message') == 'User deleted successfully'
    assert response.status_code == 200

    client.put(
        f"""/admin/user?id={test_cache.get("borrower_2_id")}&state={borrower_2.account_state}"""
    )

### ==========================
### Admin - /suspend-user
### ==========================

@pytest.mark.parametrize(
    ("id", "reason", "error", "status_code"), (
        (None, "test reason", "Missing id field", 400),
        ("borrower_2", None, "Missing reason field", 400),
        ("test", "test", "Invalid id test", 400),
        (123123, "reason", "User id 123123 not found", 404)
    )
)
def test_suspend_user_bad(client_factory, id, reason, error, status_code):
    client = client_factory("admin")

    if id == "borrower_2":
        id = test_cache.get("borrower_2_id")

    response = client.post(
        f"""/admin/suspend-user""",
        json = {
            "id": id,
            "reason": reason
        }
    )

    assert response.json.get("error") == error
    assert response.status_code == status_code

def test_suspend_user_good(client_factory):
    client = client_factory('admin')

    response = client.post(
        f'/admin/suspend-user',
        json = {
            'id': test_cache.get('borrower_2_id'),
            'reason': 'testreason'
        }
    )

    assert response.json.get('message') == 'User suspended successfully'
    assert response.status_code == 200

### ==========================
### Admin - /reinstate-user
### ==========================

@pytest.mark.parametrize(
    ("id", "error", "status_code"), (
        (None, "Missing id field", 400),
        ("test", "Invalid id test", 400),
        (123123, "User id 123123 not found", 404)
    )
)
def test_reinstate_user_bad(client_factory, id, error, status_code):
    client = client_factory("admin")

    response = client.post(
        f"""/admin/reinstate-user""",
        json = {
            "id": id
        }
    )

    assert response.json.get("error") == error
    assert response.status_code == status_code

def test_reinstate_user_good(client_factory):
    client = client_factory('admin')

    response = client.post(
        f'/admin/reinstate-user',
        json = {
            "id": test_cache.get("borrower_2_id")
        }
    )

    assert response.json.get('message') == 'User reinstated successfully'
    assert response.status_code == 200

### ==========================
### Admin - GET /app-setting
### ==========================

def test_get_setting_good(client_factory):
    client = client_factory('admin')

    response = client.get(
        '/admin/app-setting'
    )

    assert 'reminder_every_x_days' in response.json.get('data')
    assert 'reminder_x_days_before_due' in response.json.get('data')
    assert response.status_code == 200

### ==========================
### Admin - PUT /app-setting
### ==========================

@pytest.mark.parametrize(
    ("key", "value", "error", "status_code"), (
        (None, "15", "Missing key field", 400),
        ("reminder_every_x_days", None, "Missing value field", 400),
        ("test", "15", "Key test not found", 404)
    )
)
def test_update_setting_bad(client_factory, key, value, error, status_code):
    client = client_factory("admin")

    response = client.put(
        f"""/admin/app-setting""",
        json = {
            'key': key,
            'value': value
        }
    )

    assert response.json.get("error") == error
    assert response.status_code == status_code

def test_update_setting_good(client_factory):
    client = client_factory("admin")

    response = client.put(
        f"""/admin/app-setting""",
        json = {
            'key': 'reminder_every_x_days',
            'value': '15'
        }
    )

    assert response.json.get("message") == 'Setting updated successfully'

