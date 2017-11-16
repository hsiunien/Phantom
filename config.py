import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_NAME = 'Zheer.me'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SUBJECT_PREFIX = '[这儿]'
    MAIL_SENDER = '{app_name} <{mail_username}>' \
        .format(app_name=APP_NAME,
                mail_username=os.environ.get('MAIL_USERNAME'))
    ADMIN = os.environ.get('ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = 80
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    POSTS_PER_PAGE = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATA_BASE_URI = 'sqlite:///' + os.path.join(base_dir, 'data-test.sqlite')


class ProductionConfig(Config):
    TESTING = True
    SQLALCHEMY_DATA_BASE_URI = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
