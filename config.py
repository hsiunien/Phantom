import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    if os.path.exists('.env'):
        print('set up environment from .env')
        with open('.env') as f:
            for line in f.readlines():
                var = line.strip().split("=")
                if len(var) == 2:
                    # print('set local env:%s=%s' % (var[0].strip(), var[1].strip()))
                    os.environ[var[0].strip()] = var[1].strip()

    APP_NAME = os.environ.get('APP_NAME') or 'Zheer.me'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SUBJECT_PREFIX = os.environ.get('MAIL_SUBJECT_PREFIX') or '[这儿]'
    MAIL_SENDER = '{app_name} <{mail_username}>' \
        .format(app_name=APP_NAME,
                mail_username=os.environ.get('MAIL_USERNAME'))
    ADMIN = os.environ.get('ADMIN')
    # 启用缓慢查询的记录
    QUERY_DB_TIME_OUT = 0.05
    SQLALCHEMY_RECORD_QUERIES = True

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT') or 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    POSTS_PER_PAGE = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.environ.get('DB_USER') + ':' + os.environ.get(
        'DB_PWD') + '@localhost/zheer_dev'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.environ.get('DB_USER') + ':' + os.environ.get(
        'DB_PWD') + '@localhost/zheer_dev'


class ProductionConfig(Config):
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.environ.get('DB_USER') + ':' + os.environ.get(
        'DB_PWD') + '@localhost/zheer'

    @classmethod
    def init_app(cls, app):
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                                   fromaddr=cls.MAIL_SENDER,
                                   toaddrs=[cls.ADMIN],
                                   subject=cls.MAIL_SUBJECT_PREFIX + ' Application Error',
                                   credentials=credentials,
                                   secure=secure
                                   )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'unixconfig': UnixConfig,
    'default': UnixConfig
}
