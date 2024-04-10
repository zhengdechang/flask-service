import os


class BaseConfig:

    def __init__(self):
        pass

    DEBUG = False
    TESTING = False
    JWT_WHITE_LIST = []
    AUTH_CONFIG = {
        'JWT_SECRET': os.environ.get('JWT_SECRET', 'flask_app'),
        'JWT_ALGORITHM': os.environ.get('JWT_ALGORITHM', 'HS256'),
        'ACCESS_TOKEN_MAX_AGE': 10 * 60,    # 10 minutes
        'REFRESH_TOKEN_MAX_AGE': 3 * 60 * 60    # 1 hour
    }


class ProductionConfig(BaseConfig):
    ENV = 'production'


class DevelopmentConfig(BaseConfig):
    ENV = 'development'
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
