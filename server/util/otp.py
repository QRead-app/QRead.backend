import secrets
from server.util.extensions import otp_cache
from server.exceptions import RecordNotFoundError

class OTP:
    def __init__(self):
        pass

    def generate_otp(self, user_id: int) -> str:
        otp = ''.join(secrets.choice("0123456789") for _ in range(6))
        otp_cache.set(user_id, otp)

        return otp

    def verify_otp(self, user_id: int, otp: str) -> bool:
        cached = otp_cache.get(user_id)

        if cached is None:
            raise RecordNotFoundError()

        verication = cached == otp

        if verication:
            otp_cache.delete(user_id)

        return verication
    
otp = OTP()