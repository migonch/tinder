import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(16)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PHOTO_FOLDER = 'users_photos'
    SECURITY_PASSWORD_SALT = os.urandom(16)

    MAIL_SERVER = 'relay.mipt.ru'
    MAIL_PORT = 25
    #MAIL_USE_TLS = False
    #MAIL_USE_SSL = True
    #MAIL_USERNAME = 'goncharov.myu@phystech.edu'
    #MAIL_PASSWORD = 'firair1998'
    MAIL_DEFAULT_SENDER = 'goncharov.myu@phystech.edu'
