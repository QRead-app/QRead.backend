import logging
from flask import Flask, g, jsonify
from flask_cors import CORS
from server.model.service.notification_service import due_date_reminder
from server.util.extensions import otp_cache, mailer, forgot_password_cache, new_librarian_cache, scheduler
from server.exceptions import DatabaseError
from server.model.db import DB
from server.route.admin.admin import admin
from server.route.borrower.borrower import borrower
from server.route.librarian.librarian import librarian
from server.route.common_route import common
from server.model.seed import seed_db
from tests.extensions import test_cache
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger

def create_app(env: str = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=False)

    if env is not None:
        app.config["ENVIRONMENT"] = env
    env = app.config["ENVIRONMENT"]

    if app.config["ENVIRONMENT"] == 'development':
        app.config.from_object('server.config.DevelopmentConfig')
    if app.config["ENVIRONMENT"] == 'production':
        app.config.from_object('server.config.ProductionConfig')
    if app.config["ENVIRONMENT"] == 'testing':
        app.config.from_object('server.config.TestingConfig')
        app.config["CONNECTION_STRING"] = app.config["TEST_CONNECTION_STRING"]
        test_cache.init_app(app)
        
    CORS(
        app,
        supports_credentials=True
    )
    seed_db.init_app(app)
    otp_cache.init_app(app)
    forgot_password_cache.init_app(app)
    new_librarian_cache.init_app(app)
    mailer.init_app(app)

    app.register_blueprint(admin)
    app.register_blueprint(borrower)
    app.register_blueprint(librarian)
    app.register_blueprint(common)

    @app.before_request
    def load_session():
        db = DB.get_db()
        Session = db.get_sessionmaker()
        g.Session = Session

    def due_date_reminder_job():
        with app.app_context():
            due_date_reminder()

    scheduler.add_job(
        func = due_date_reminder_job,
        id = "due_date_reminder",
        trigger = CronTrigger.from_crontab("0 16 * * *"),
        replace_existing = True
    )
    with app.app_context():
        scheduler.start()

    app.register_error_handler(
        DatabaseError,
        handle_database_error
    )
   
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(logging.INFO)

    return app

def handle_database_error(e):
    return jsonify({"error": "Internal server error"}), 500
