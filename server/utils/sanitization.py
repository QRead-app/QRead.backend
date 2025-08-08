import re

def is_email(email: str) -> bool:
    return re.search("^.+@.+[.].+$", email) != None