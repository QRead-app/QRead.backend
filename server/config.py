from datetime import timedelta

class Config:
    TESTING = False

    PROPAGATE_EXCEPTIONS = True
    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = True

    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_PARTITIONED = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes = 30)
    SESSION_REFRESH_EACH_REQUEST = True

    USE_X_SENDFILE = False
    SEND_FILE_MAX_AGE_DEFAULT = None

    TRUSTED_HOSTS = None
    SERVER_NAME = None
    
    APPLICATION_ROOT = '/'

    PREFERRED_URL_SCHEME = 'http'

    MAX_CONTENT_LENGTH = None
    MAX_FORM_MEMORY_SIZE = 500_000
    MAX_FORM_PARTS = 1_000

    CACHE_DEFAULT_TIMEOUT = 300

class ProductionConfig(Config):
    PROPAGATE_EXCEPTIONS = False
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = False

    SESSION_COOIE_SECURE = True

    TRUSTED_HOSTS = None
    SERVER_NAME = None

    PREFERRED_URL_SCHEME = 'https'

class DevelopmentConfig(Config):
    pass

class TestingConfig(Config):
    TESTING = True