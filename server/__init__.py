from flask import Flask, g, jsonify
from flask_cors import CORS
from server.util.extensions import *
from server.exceptions import DatabaseError
from server.model.db import DB
from server.route.admin.admin import admin
from server.route.borrower.borrower import borrower
from server.route.librarian.librarian import librarian
from server.route.common_route import common
from server.model.seed import seed_db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=False)

    if app.config["ENVIRONMENT"] == 'development':
        app.config.from_object('server.config.DevelopmentConfig')
        CORS(app)
    if app.config["ENVIRONMENT"] == 'production':
        app.config.from_object('server.config.ProductionConfig')
    if app.config["ENVIRONMENT"] == 'testing':
        app.config.from_object('server.config.TestingConfig')
        app.config["CONNECTION_STRING"] = app.config["TEST_CONNECTION_STRING"]
        CORS(app)

    seed_db.init_app(app)
    otp_cache.init_app(app)
    mailer.init_app(app)

    app.register_blueprint(admin)
    app.register_blueprint(borrower)
    app.register_blueprint(librarian)
    app.register_blueprint(common)

    db = DB(app.config["CONNECTION_STRING"])
    Session = db.get_sessionmaker()

    @app.before_request
    def load_session():
        g.Session = Session

    app.register_error_handler(
        DatabaseError,
        handle_database_error
    )

    return app

def handle_database_error(e):
    return jsonify({"error": "Internal server error"}), 500