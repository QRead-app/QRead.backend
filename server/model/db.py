from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DB:
    def __init__(self, connection_string, autocommit=True):
        self.engine = create_engine(connection_string)
        self.session = sessionmaker(self.engine, autocommit=autocommit)

    def get_sessionmaker(self) -> sessionmaker:
        return self.session