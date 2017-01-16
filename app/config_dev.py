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
SECRET_KEY = 'T1m55pw4m55FA'
SECURITY_PASSWORD_SALT = 'Saltines_are_saltier'

#pagination NOT IMPLEMENTED YET
POSTS_PER_PAGE = 5

#Flask-Mail Config
MAIL_SERVER = 'smtp.zoho.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'noreply@eggzlist.com' #SET MANUALLY, KEEP OFF GITHUB
MAIL_PASSWORD = '!234Abcdnoreply'
MAIL_DEFAULT_SENDER = 'noreply@eggzlist.com'
