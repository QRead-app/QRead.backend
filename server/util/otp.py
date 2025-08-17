import secrets
import string
from server.util.extensions import otp_cache, forgot_password_cache
from server.exceptions import IncorrectCredentialsError, RecordNotFoundError

class OTP:
    def __init__(self):
        pass

    def generate_otp(self, user_id: int) -> str:
        otp = ''.join(secrets.choice("0123456789") for _ in range(6))
        otp_cache.set(user_id, otp)

        return otp

    def generate_forgot_password_otp(self, user_id: str) -> str:
        alphabet = string.ascii_letters + string.digits 
        secure_string = ''.join(secrets.choice(alphabet) for i in range(32))

        forgot_password_cache.set(secure_string, user_id)

        return secure_string

    def verify_otp(self, user_id: int, otp: str) -> bool:
        cached = otp_cache.get(user_id)

        if cached is None:
            raise RecordNotFoundError()

        verication = cached == otp

        if verication:
            otp_cache.delete(user_id)

        return verication
    
    def verify_forgot_password(self, secret: str) -> int:
        cached = forgot_password_cache.get(secret)

        if cached is None:
            raise IncorrectCredentialsError()
        
        otp_cache.delete(secret)

        return cached
    
otp = OTP()