from flask import current_app, g
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

class DB:
    def __init__(self):
        self.engine = create_engine(current_app.config["CONNECTION_STRING"])
        self.session = sessionmaker(self.engine)

    def get_sessionmaker(self) -> sessionmaker:
        return self.session
    
    def get_engine(self) -> Engine:
        return self.engine
    
    @staticmethod
    def get_db():
        if "db" not in g:
            g.db = DB()

        return g.db