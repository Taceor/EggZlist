import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_mail import Mail
import flask_resize

app = Flask(__name__)
app.config.from_object('config')
app.debug = True
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = u"You must be logged in to access that page."
flask_resize.Resize(app)
mail = Mail(app)

from app import views, models
