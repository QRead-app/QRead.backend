from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError
from flask import Flask

from server.exceptions import DatabaseError, IncorrectCredentialsError

class Hasher:
    def __init__(self):
        # Preset according to recommendation from 
        # https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
        self.hasher = PasswordHasher(
            time_cost = 2,
            memory_cost = 19456,
            parallelism = 1,
        )

    def hash(self, password: str) -> str:
        try:
            hash = self.hasher.hash(password)
        except HashingError as e:
            raise DatabaseError()

        return hash
    
    def verify(self, hash: str, password: str) -> bool:
        try:    
            verification = self.hasher.verify(hash, password)
        except VerifyMismatchError as e:
            raise IncorrectCredentialsError()
        
        return verification
    
    def need_rehash(self, hash: str) -> bool:
        return self.hasher.check_needs_rehash(hash)