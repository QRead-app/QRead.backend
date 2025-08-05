from flask import Flask

def create_app(config_name='development'):
    app = Flask(__name__, instance_relative_config=True)

    if config_name == 'development':
        app.config.from_object('config.DevelopmentConfig')
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    if config_name == 'testing':
        app.config.from_object('config.TestingConfig')

    app.config.from_pyfile('config.py', silent=True)
    
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app