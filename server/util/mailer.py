from flask_mail import Message
from server.model.tables import Book, User
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

    def send_forgot_password(self, to: str, secret: str, redirect: str) -> None:
        if not User.is_email(to):
            raise ValueError()
        
        msg = Message(
            subject = "QRead OTP",
            sender = "noreply@QRead.com",
            recipients = [to],
            body = f"Reset your password: {redirect}?secret={secret}"
        )

        mail.send(msg)

    def send_new_librarian(self, to: str, secret: str, redirect: str) -> None:
        if not User.is_email(to):
            raise ValueError()
        
        msg = Message(
            subject = "QRead OTP",
            sender = "noreply@QRead.com",
            recipients = [to],
            body = f"Create new librarian account: {redirect}?secret={secret}"
        )

        mail.send(msg)

    def send_reminder(self, to: str, book: Book, days_left: int) -> None:
        if not User.is_email(to):
            raise ValueError()
        
        msg = Message(
            subject = "QRead OTP",
            sender = "noreply@QRead.com",
            recipients = [to],
            body = f"Reminder: Your book {book.title} will be due in {days_left} day(s)."
        )

        mail.send(msg)
        
mailer = Mailer()