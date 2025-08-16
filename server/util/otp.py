import secrets
from server import otp_cache

class OTP:
    def __init__(self):
        pass

    def generate_otp(self, user_id: int) -> int:
        otp = ''.join(secrets.choice("0123456789") for _ in range(6))
        otp_cache.set(user_id, otp)

        return otp

    def verify_otp(self, user_id: int, otp: int) -> bool:
        verication = otp_cache.get(user_id) == otp

        if verication:
            otp_cache.delete(user_id)

        return verication