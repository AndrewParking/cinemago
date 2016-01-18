class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = '4$a6@5f$64a@#dsfs&^$DT#^D@FDF#@&^%^t^GF'
    SHELL_BANNER = '\n *** Welcome to Cinemago Shell *** \n'
    AUTH_TOKEN_EXPIRATION_TIME = 24*60*60
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'popow.andrej2009@gmail.com'
    MAIL_PASSWORD = 'homm1994'
    MAIL_SENDER = 'Cinemago Administration'
    SCRAPY_PROJECT_NAME = 'cinemago_parse'
    DEFAULT_SPIDER_NAME = 'tutby'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://admin:homm1994@localhost/dev_db'
    SCRAPY_SERVER_URL = 'http://localhost:6000/'
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://admin:homm1994@localhost/test_db'
    TESTING = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://admin:homm1994@localhost/cinemago_db'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    # default one
    'default': DevelopmentConfig,
}
