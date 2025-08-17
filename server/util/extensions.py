from flask_caching import Cache
from flask_mail import Mail

otp_cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
forgot_password_cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
mailer = Mail()