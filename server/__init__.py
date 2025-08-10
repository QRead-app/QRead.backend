from flask import Flask, g
from server.model.db import DB
from server.route.admin.admin import admin
from server.route.borrower.borrower import borrower
from server.route.librarian.librarian import librarian
from server.route.common_route import common

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=False)

    if app.config["ENVIRONMENT"] == 'development':
        app.config.from_object('server.config.DevelopmentConfig')
    if app.config["ENVIRONMENT"] == 'production':
        app.config.from_object('server.config.ProductionConfig')
    if app.config["ENVIRONMENT"] == 'testing':
        app.config.from_object('server.config.TestingConfig')

    from .model.seed import seed_db
    seed_db.init_app(app)

    app.register_blueprint(admin)
    app.register_blueprint(borrower)
    app.register_blueprint(librarian)
    app.register_blueprint(common)

    db = DB(app.config["CONNECTION_STRING"])
    Session = db.get_sessionmaker()

    @app.before_request
    def load_session():
        g.Session = Session

    return app