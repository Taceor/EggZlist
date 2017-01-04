# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextAreaField, StringField, SelectMultipleField, FileField,\
                    BooleanField, SubmitField, SelectField, PasswordField,\
                    FormField, FieldList
from wtforms.validators import InputRequired, Optional, Length, Email

class ContactInfoForm(Form):
    email = StringField('Email', [InputRequired(), Email()])
    confirm = StringField('Confirm', [InputRequired()])
    viewable = BooleanField()
    zipcode = StringField('Zipcode', [InputRequired()])
    address = StringField('Address')
    city = StringField('City')
    state = StringField('State')
    phone = StringField('Phone')
    name = StringField('Name', [InputRequired(), Length(min=4)])

class ItemInfoForm(Form):
    title = StringField('Title', [InputRequired()])
    category = SelectField('Category', choices=[('Dairy', 'Dairy'), ('Fruit', 'Fruit'), ('Vegetable', 'Vegetable'), ('Grain', 'Grain'), ('Protein', 'Protein'), ('Other', 'Other')])
    price = StringField('Price', [InputRequired()])
    price_type = SelectField('Price Type', choices=[('total', 'Total'), ('each', 'Each')])
    description = TextAreaField('Description')
    """
        PICTURES
        OPTIONS
    """

class PhotoForm(Form):
    photo_file = FileField()

class ListingPhotosForm(Form):
    photos = FieldList(FormField(PhotoForm), min_entries=1)
    add_photo = SubmitField('Add photo')

class LoginForm(Form):
    username = StringField('Nickname', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])

class NewUserForm(Form):
    username = StringField('Nickname', [InputRequired(), Length(min=4)]) #TODO Check Uniqueness
    email = StringField('Email', [InputRequired(), Email()])
    email_confirm = StringField('Email', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    password_confirm = PasswordField('Password', [InputRequired()])

class AboutUserForm(Form):
    about = TextAreaField('About')
