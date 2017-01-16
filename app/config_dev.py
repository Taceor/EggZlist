import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
ALLOWED_EXTENSIONS = set(['.png', '.jpg', '.jpeg'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

RESIZE_URL = '/static/uploads/'
RESIZE_ROOT = os.path.join(basedir, 'static/uploads/')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'public_secret'
SECURITY_PASSWORD_SALT = 'public_salt'

#Flask-Mail Config
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'me@localhost.com'
MAIL_PASSWORD = 'pusblic_password'
MAIL_DEFAULT_SENDER = 'me@localhost.com'
