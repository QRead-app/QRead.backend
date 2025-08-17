from flask_mail import Message
from server.model.tables import User
from server.util.extensions import mailer as mail

class Mailer:
    def __init__(self):
        pass

    def send_otp(self, to: str, otp: str) -> None:
        if not User.is_email(to):
            raise ValueError()
        
        msg = Message(
            subject = "QRead OTP",
            sender = "noreply@QRead.com",
            recipients = [to],
            body = f"Your OTP is {otp}"
        )

        mail.send(msg)

    def send_forgot_password(self, to: str, secret: str) -> None:
        if not User.is_email(to):
            raise ValueError()
        
        msg = Message(
            subject = "QRead OTP",
            sender = "noreply@QRead.com",
            recipients = [to],
            body = f"Your reset password secret is {secret}"
        )

        mail.send(msg)

    def send_new_librarian(self, to: str, secret: str) -> None:
        if not User.is_email(to):
            raise ValueError()
        
        msg = Message(
            subject = "QRead OTP",
            sender = "noreply@QRead.com",
            recipients = [to],
            body = f"Your new librarian account secret is {secret}"
        )

        mail.send(msg)
        
mailer = Mailer()