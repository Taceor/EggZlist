# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

saved_posts = db.Table('saved_posts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'))
    )

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    category = db.Column(db.String(200))
    price = db.Column(db.Float)
    price_type = db.Column(db.String(10))
    post_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="items")
    photos = db.relationship('Photo', backref='item', lazy='dynamic')
    has_photos = db.Column(db.Boolean)
    flags = db.Column(db.Integer)
    user_saves = db.relationship('User', secondary=saved_posts,
        backref=db.backref('saves', lazy='dynamic'))

    def __init__(self, title, category, price, price_type, description, user_id):
        self.title = title
        self.category = category
        self.price = price
        self.price_type = price_type
        self.post_date = datetime.today()
        self.description = description
        self.user_id = user_id
        self.has_photos = False

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.title)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    featured = db.Column(db.Boolean)
    path = db.Column(db.String(255))
    full_path = db.Column(db.String(511))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    def __init__(self, item_id, path, full_path):
        self.item_id = item_id
        self.path = path
        self.full_path = full_path
        self.featured = False

    def __repr__(self):
        return "<{} for listing {}, path = {}>".format(self.__class__.__name__, self.item_id, self.path)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, unique=True)
    username = db.Column(db.String(42))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    pw_hash = db.Column(db.String(255))
    registered_on = db.Column(db.DateTime)
    about = db.Column(db.Text())
    is_verified = db.Column(db.Boolean, default=False)
    verfied_on = db.Column(db.DateTime)
    sent_verification_on = db.Column(db.DateTime)

    # # VENDOR STUFF # #
    is_vendor = db.Column(db.Boolean, default=False)
    viewable = db.Column(db.Boolean)
    zipcode = db.Column(db.Integer)
    street = db.Column(db.String(200))
    city = db.Column(db.String(200))
    state = db.Column(db.String(100))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    has_phone = db.Column(db.Boolean)
    phone_number = db.Column(db.String(20))
    items = db.relationship('Item', back_populates="user")
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.registered_on = datetime.now()

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username) 
