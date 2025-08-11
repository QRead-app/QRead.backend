import pytest

from flask import current_app, g
from tests.test_data import *


"""
    Borrower - /register
"""

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
        "/borrower/register",
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

"""
    Borrower - /borrow
"""

def test_borrow_bad_unauthorized(client):
    response = client.post(
        "/borrower/borrow",
        json = {
            "books": ["123"]
        }
    )

    assert response.json.get("error") == "Unauthorized"
    assert response.status_code == 401

@pytest.mark.parametrize(('books', 'message', "code"), (
    ({}, "Missing field", 400),
    ({"books": ["1"]}, "Book 1 does not exist", 400),
    ({"books": ["2", "1"]}, "Book 2 does not exist", 400)
))
def test_borrow_bad(borrower_client, books, message, code):
    response = borrower_client.post(
        "/borrower/borrow",
        json = books
    )

    assert response.json.get("error") == message
    assert response.status_code == code

def test_borrow_good(borrower_client):
    response = borrower_client.post(
        "/borrower/borrow",
        json = {
            "books": [current_app.config["test_book"]["id"]]
        }
    )

    assert response.json.get("message") == "Book(s) borrowed successfully"
    assert response.status_code == 200

def test_borrow_bad_borrowed(borrower_client):
    response = borrower_client.post(
        "/borrower/borrow",
        json = {
            "books": [current_app.config["test_book"]["id"]]
        }
    )

    assert response.json.get("error") == f"Book {current_app.config['test_book']['id']} has already been borrowed"
    assert response.status_code == 400

"""
    Borrower - /get-borrowed-books
"""

def test_get_borrowed_bad_unauthorized(client):
    response = client.get(
        "/borrower/get-borrowed-books"
    )

    assert response.json.get("error") == "Unauthorized"
    assert response.status_code == 401

def test_get_borrowed_bad_no_borrowed(borrower_2_client):
    response = borrower_2_client.get(
        "/borrower/get-borrowed-books"
    )

    assert response.status_code == 204

def test_get_borrowed_good(borrower_client):
    response = borrower_client.get(
        "/borrower/get-borrowed-books"
    )
    
    assert response.json.get("message") == "Borrowed book(s) retrieved"
    assert response.status_code == 200
    assert response.json.get("data")[0]["id"]== current_app.config["test_book"]["id"]
