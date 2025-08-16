from flask_mail import Message
from server import mail
from server.exceptions import ParameterError
from server.model.tables import User

class Mailer:
    def __init__(self):
        self.mailer = mail

    def send_otp(self, to: str, otp: int) -> None:
        if not User.is_email(to):
            raise ValueError()
        
        msg = Message(
            subject = "QRead OTP",
            sender = "noreply@QRead.com",
            recipients = [to],
            body = f"Your OTP is {otp}"
        )

        self.mailer.send(msg)
        
