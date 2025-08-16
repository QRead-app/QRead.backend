from flask import current_app
from flask_mail import Mail, Message
from server.model.tables import User

class Mailer:
    def __init__(self):
        self.mailer: Mail = current_app.extensions["mail"]

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
        
