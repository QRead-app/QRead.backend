<a id="readme-top"></a>

<div align="center">
  <h3 align="center">QRead.backend</h3>

  <p align="center">
    Backend for our QRead FYP project
</div>

<!-- ABOUT THE PROJECT -->
## About The Project

This project includes our backend built with Flask, providing all the necessary APIs to support and run our application.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Flask][Flask]][Flask-url]
* [![SQLAlchemy][SQLAlchemy]][SQLalchemy-url]
* [![Alembic][Alembic]][Alembic-url]
* [![Poetry][Poetry]][Poetry-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

1. Python version >= 3.11
2. Set up a virtual environment
    ```sh
    python -m venv C:\path\to\new\virtual\environment
    ```
3. Activate virtual environment
    ```sh
    C:\path\to\virtual\environment\Scripts\activate
    ``` 
4. Poetry installation
    ```sh
    pip install poetry
    ```

### Project Installation


Installing dependencies
  ```sh
  poetry install
  ```

### Configuring 
Make a ```config.py``` file in ```instance/```
```python
SECRET_KEY = ''
CONNECTION_STRING = ''
ENVIRONMENT = "development"
```
* Please generate a secure SECRET_KEY as it will be used to cryptographically sign cookies
* Connection string will be the connection url to the database
* More configs can be found in ```server/config.py``` which do not require additional configurations

### Setting up DB
#### Running a migration
Skip this and <b>Seeding the database</b> if you are using Kayne's neondb as I have already set everything up

- To upgrade to the latest migration
  ```sh
  alembic upgrade head
  ```
- Or downgrade to the base
  ```sh
  alembic downgrade base
  ```
#### Update the database
- Update ```server/model/tables.py``` and run
  ```sh
  alembic revision -m "update information"
  ```
- Or run below to autogenerate the migration
  ```sh
  alembic revision --autogenerate -m "update information"
  ```
Remember to check the generated revision in ```alembic/version/{version_number}_update_information.py``` as the changes might not be reflected accurately

#### Seeding the database
Skip this if you are using Kayne's neondb as I have already set everything up

- Seed command
  ```sh
  Flask --app seed-db run
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
Run the server with
  ```sh
  Flask --app server run --debug
  ```
### API information
Database error will be received for all requests if there is something wrong with accessing the database
  ```
  500 Internal Server Error

  {
    "error": "Database operation failed"
  }
  ```
### Borrower
<b>POST</b> ```/borrower/login``` - Borrower log in
  * Request
    ```
    Content-Type: application/json

    {
      "email": "value",
      "password": "value"
    }
    ```
  * Responses
    * Login success
      ````
      200 OK

      {
        "message": "Login successful"
      }

      Set-Cookie: session
      ````
    * Wrong path e.g. /borrow/login
      ```
      404 Not Found

      {
        "error": "Invalid path borrow"
      }
      ```
    * Wrong email or password
      ```
      401 Unauthorized

      {
        "error": "Authentication failed"
      }
      ```
  ---
<b>POST</b> ```/logout``` - Borrower log out
  * Request
      ```
      Send the cookie: session
      ```
  * Responses
    * Logout success
      ````
      200 OK

      {
        "message": "Logout successful"
      }
      ````
    * Borrower not logged in
      ````
      204 No content

      {
        "message": "No active session"
      }
      ````
  ---
<b>POST</b> ```/borrower/register``` - Borrower register
  * Request
      ```
      Content-Type: application/json

    {
      "name" : "value",
      "email": "value",
      "password": "value"
    }
      ```
  * Responses
    * Registered
      ````
      200 OK

      {
        "message": "Registered"
      }
      ````
    * Not an email
      ````
      400 Bad Request

      {
        "error": "Invalid email"
      }
      ````
    * Email already registered
      ````
      400 Bad request

      {
        "error": "The email provided is already registered"
      }
      ````
  
  ---
#### API below requires authentication to continue
  ```
  Unauthenticated

  401 Unauthorized

  {
    "error": "Authentication failed"
  }
  ```
  ---

<b>POST</b> ```/borrower/borrow``` - Borrow books
  * Request
      ```
      Content-Type: application/json

    {
      "books" : ["book_id", "book_id"]
    }
      ```
  * Responses
    * Books borrowed success
      ```
      200 OK

      {
        "message": "Book(s) borrowed successfully"
      }
      ```
    * Book does not exist or has already been borrowed e.g. id=12
      ````
      400 Bad Request

      {
        "error": "12 has already been borrowed or does not exist"
      }
      ````
  ---

<b>GET</b> ```/borrower/get-borrowed-books``` - Get borrowed books
  * Responses
    * Borrowed book objects
      ```
      200 OK

      {
        "message": "Borrowed book(s) retrieved",
        "data": [
          {
            "id": "value",
            "title: "value",
            "description": "value",
            "author": "value",
            "condition": "value"
          },
          {
            "id": "value",
            "title: "value",
            "description": "value",
            "author": "value",
            "condition": "value"
          },
        ]
      }
      ```
    * Book does not exist or has already been borrowed e.g. id=12
      ````
      400 Bad Request

      {
        "error": "12 has already been borrowed or does not exist"
      }
      ````
    * No books borrowed
      ````
      204 No content

      {
        "message": "No books found"
      }
      ````
  ---

<b>GET</b> ```/borrower/get-fines``` - Get unpaid fines
  * Responses
    * Unpaid fine objects
      ```
      200 OK

      {
        "message": "Fine(s) retrieved",
        "data": [
          {
            "id": "value",
            "user_id: "value",
            "transaction_id": "value",
            "amount": "value",
            "date": "value",
            "paid": "value",
            "book": 
              {
                "id": "value",
                "title: "value",
                "description": "value",
                "author": "value",
                "condition": "value"
              }
          },
          {
            "id": "value",
            "user_id: "value",
            "transaction_id": "value",
            "amount": "value",
            "date": "value",
            "paid": "value",
            "book": 
              {
                "id": "value",
                "title: "value",
                "description": "value",
                "author": "value",
                "condition": "value"
              }
          },
        ]
      }
      ```
    * No pending fines
      ````
      204 No content

      {
        "message": "No fines found"
      }
      ````
  ---

<b>POST</b> ```/borrower/pay-fine``` - Pay fine
  
  ---


### Librarian
<b>POST</b> ```/librarian/login``` - Borrower log in
  * Request
    ```
    Content-Type: application/json

    {
      "email": "value",
      "password": "value"
    }
    ```
  * Responses
    * Login success
    ````
    200 OK

    {
      "message": "Login successful"
    }

    Set-Cookie: session
    ````
    * Wrong path e.g. /libraria/login
    ```
    404 Not Found

    {
      "error": "Invalid path libraria"
    }
    ```
    * Wrong email or password
    ```
    401 Unauthorized

    {
      "error": "Authentication failed"
    }
    ```
    * Database error
    ```
    500 Internal Server Error

    {
      "error": "Database operation failed"
    }
    ```
  ---
<b>POST</b> ```/logout``` - Librarian log out
  * Request
      ```
      Send the cookie: session
      ```
  * Responses
    * Logout success
    ````
    200 OK

    {
      "message": "Logout successful"
    }
    ````
    * Librarian not logged in
    ````
    204 No content

    {
      "message": "No active session"
    }
    ````
  ---    
  
### Admin
<b>POST</b> ```/admin/login``` - Admin log in
  * Request
    ```
    Content-Type: application/json

    {
      "email": "value",
      "password": "value"
    }
    ```
  * Responses
    * Login success
    ````
    200 OK

    {
      "message": "Login successful"
    }

    Set-Cookie: session
    ````
    * Wrong path e.g. /admi/login
    ```
    404 Not Found

    {
      "error": "Invalid path admi"
    }
    ```
    * Wrong email or password
    ```
    401 Unauthorized

    {
      "error": "Authentication failed"
    }
    ```
    * Database error
    ```
    500 Internal Server Error

    {
      "error": "Database operation failed"
    }
    ```
  ---
<b>POST</b> ```/logout``` - Admin log out
  * Request
      ```
      Send the cookie: session
      ```
  * Responses
    * Logout success
    ````
    200 OK

    {
      "message": "Logout successful"
    }
    ````
    * Admin not logged in
    ````
    204 No content

    {
      "message": "No active session"
    }
    ````
  ---

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
[Poetry]: https://img.shields.io/badge/Poetry-2.1.4-blue
[Poetry-url]: https://python-poetry.org/
[Flask]: https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=Flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/stable/
[SQLAlchemy]: https://img.shields.io/badge/sqlalchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white
[SQLAlchemy-url]: https://www.sqlalchemy.org/
[Alembic]: https://img.shields.io/badge/Alembic-1.16.4-blue
[Alembic-url]: https://alembic.sqlalchemy.org/en/latest/
