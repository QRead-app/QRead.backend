from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DB:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.session = sessionmaker(self.engine)

    def get_sessionmaker(self) -> sessionmaker:
        return self.session