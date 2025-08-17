import pytest

from flask import current_app, g
from tests.test_data import *


### ==========================
### Borrower - /register
### ==========================

@pytest.mark.parametrize(('name', 'email', 'password', 'message', "code"), (
    (None, 'testtest@test.com', "Admin", "Missing name field", 400),
    ("NAME", None, "admin", 'Missing email field', 400),
    ('test123', "test@test.com", None, 'Missing password field', 400),
    ("NAME", "test.com", "test123", 'Invalid email test.com', 400),
    (test_borrower.name, test_borrower.email, "borrower", f'Email {test_borrower.email} is already registered', 400),
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

### ==========================
### Borrower - /borrow
### ==========================

def test_borrow_bad_unauthorized(client):
    response = client.post(
        "/borrower/borrow",
        json = {
            "book_ids": ["123"]
        }
    )

    assert response.json.get("error") == "Unauthorized"
    assert response.status_code == 401

@pytest.mark.parametrize(('books', 'message', "code"), (
    ({}, "Missing book_ids field", 400),
    ({"book_ids": ["1"]}, "Book id 1 not found", 400),
    ({"book_ids": ["2", "1"]}, "Book id 2 not found", 400)
))
def test_borrow_bad(client_factory, books, message, code):
    borrower_client = client_factory("borrower")
    response = borrower_client.post(
        "/borrower/borrow",
        json = books
    )

    assert response.json.get("error") == message
    assert response.status_code == code

def test_borrow_good(client_factory):
    borrower_client = client_factory("borrower")
    response = borrower_client.post(
        "/borrower/borrow",
        json = {
            "book_ids": [current_app.config["test_book"]["id"]]
        }
    )

    assert response.json.get("message") == "Book(s) borrowed successfully"
    assert response.status_code == 200

def test_borrow_bad_borrowed(client_factory):
    borrower_client = client_factory("borrower")
    response = borrower_client.post(
        "/borrower/borrow",
        json = {
            "book_ids": [current_app.config["test_book"]["id"]]
        }
    )
    
    assert response.json.get("error") == f"Book id {current_app.config['test_book']['id']} has already been borrowed"
    assert response.status_code == 400

### ==========================
### Borrower - /borrowed-books
### ==========================

def test_get_borrowed_bad_unauthorized(client):
    response = client.get(
        "/borrower/borrowed-books"
    )

    assert response.json.get("error") == "Unauthorized"
    assert response.status_code == 401

def test_get_borrowed_bad_no_borrowed(client_factory):
    borrower_client = client_factory("borrower2")
    response = borrower_client.get(
        "/borrower/borrowed-books"
    )

    assert response.json.get("message") == "No books found"
    assert response.status_code == 200

def test_get_borrowed_good(client_factory):
    borrower_client = client_factory("borrower")
    response = borrower_client.get(
        "/borrower/borrowed-books"
    )
    
    assert response.json.get("message") == "Borrowed book(s) retrieved"
    assert response.status_code == 200
    assert response.json.get("data")[0]["book"]["id"] == current_app.config["test_book"]["id"]

### ==========================
### Borrower - /borrow-history
### ==========================

def test_borrow_history_good_no_history(client_factory):
    borrower_client = client_factory("borrower2")
    response = borrower_client.get(
        "/borrower/borrow-history"
    )
    
    assert response.json.get("message") == "No borrow history"
    assert response.status_code == 200
    

def test_borrow_history_good(client_factory):
    borrower_client = client_factory("borrower")
    response = borrower_client.get(
        "/borrower/borrow-history"
    )
    
    assert response.json.get("message") == "Book history retrieved"
    assert response.status_code == 200
    assert response.json.get("data")[0]["book"]["id"]== current_app.config["test_book"]["id"]
    assert "transaction" in response.json.get("data")[0]
    assert "return" in response.json.get("data")[0]