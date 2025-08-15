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

- [![Flask][Flask]][Flask-url]
- [![SQLAlchemy][SQLAlchemy]][SQLalchemy-url]
- [![Alembic][Alembic]][Alembic-url]
- [![Poetry][Poetry]][Poetry-url]

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

Make a `config.py` file in `instance/`

```python
SECRET_KEY = ''
CONNECTION_STRING = ''
ENVIRONMENT = "development"
```

- Please generate a secure SECRET_KEY as it will be used to cryptographically sign cookies
- Connection string will be the connection url to the database
- More configs can be found in `server/config.py` which do not require additional configurations

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

- Update `server/model/tables.py` and run
  ```sh
  alembic revision -m "update information"
  ```
- Or run below to autogenerate the migration
  ```sh
  alembic revision --autogenerate -m "update information"
  ```
  Remember to check the generated revision in `alembic/version/{version_number}_update_information.py` as the changes might not be reflected accurately

#### Seeding the database

Skip this if you are using Kayne's neondb as I have already set everything up

- Seed command
  ```sh
  Flask --app server seed-db
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Run the server with

```sh
Flask --app server run --debug
```

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
