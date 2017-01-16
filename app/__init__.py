import os
from flask import Flask
import flask_resize
from .views.home import home
from .views.auth import auth
from .views.market import market
from .views.community import comm
from .views.admin import admin

resize = flask_resize.Resize()

def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    from app.models import db
    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()

    if config_file == 'config_dev.py':
        from app.models import User
        admin_user = User("admin", "admin@eggzlist.com", "Th151553cur3")
        admin_user.is_admin=True
        db.session.add(admin_user)
        db.session.commit()

    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(market)
    app.register_blueprint(comm)
    app.register_blueprint(admin)
    app.debug = True

    from app.login_manager import lm
    lm.init_app(app)
    lm.login_view = 'auth.login'
    lm.login_message = u"You must be logged in to access that page."
    
    from app.email import mail
    mail.init_app(app)
    
    resize.init_app(app)

    return app

#from app import views, models
