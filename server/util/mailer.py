from flask_mail import Message
from server.model.tables import User
from server.util.extensions import mailer as mail

class Mailer:
    def __init__(self):
        pass

    def send_otp(self, to: str, otp: int) -> None:
        if not User.is_email(to):
            raise ValueError()
        
        msg = Message(
            subject = "QRead OTP",
            sender = "noreply@QRead.com",
            recipients = [to],
            body = f"Your OTP is {otp}"
        )

        mail.send(msg)
        
mailer = Mailer()