from flask_caching import Cache
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler

otp_cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
forgot_password_cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
new_librarian_cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
mailer = Mail()

scheduler = BackgroundScheduler()

