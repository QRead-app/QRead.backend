from flask import Flask, g
from .model.db import DB

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=False)

    if app.config["ENVIRONMENT"] == 'development':
        app.config.from_object('server.config.DevelopmentConfig')
    if app.config["ENVIRONMENT"] == 'production':
        app.config.from_object('server.config.ProductionConfig')
    if app.config["ENVIRONMENT"] == 'testing':
        app.config.from_object('server.config.TestingConfig')

    with app.app_context():
        g.DB = DB(app.config["CONNECTION_STRING"])

    from .model.seed import seed_db
    seed_db.init_app(app)

    return app