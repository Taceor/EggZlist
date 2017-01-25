# -*- coding: utf-8 -*-
import datetime
import os
import sys
from app import models
from app.token import generate_confirmation_token, confirm_token
from app.email import send_email
from sqlalchemy import asc, desc
from flask import Blueprint, redirect, url_for, current_app, request,\
                  flash, render_template, g, session, send_from_directory,\
                  jsonify
from app.config import SECRET_KEY
from app.models import Item, User, Photo, db
from app.forms import ContactInfoForm, ItemInfoForm, LoginForm, NewUserForm,\
                  AboutUserForm, ListingPhotosForm
from app.login_manager import lm
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from werkzeug import secure_filename

auth = Blueprint('auth', __name__)

@auth.route('/verify/<token>')
@login_required
def verify_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash('Account is already confirmed. Please login.', 'success')
    else:
        user.is_verified = True
        user.verified_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('Thanks for verifying your account with EggZlist!', 'success')
    return redirect(url_for('.profile', username = user.username)) 

@auth.route('/resend')
@login_required
def resend_verification():
    td = datetime.datetime.now() - g.user.sent_verification_on
    if g.user.sent_verification_on is None or \
       td > datetime.timedelta(seconds=3600):
        token = generate_confirmation_token(g.user.email)
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        html = render_template('auth/verify_email.html', verify_url=verify_url)
        subject = "EggZlist - Please verify your email"
        send_email(g.user.email, subject, html)
        flash('A new verification email has been sent.', 'success')
        g.user.sent_verification_on = datetime.datetime.now()
        db.session.add(g.user)
        db.session.commit()
    else:
        flash("Verification email already sent. Please wait a few minutes \
        before requesting another.")
    return redirect(url_for('.profile', username = g.user.username))

@auth.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@auth.before_app_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated:
        return redirect(url_for("market.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user==None:
            flash ('No such user')
            return redirect(url_for('.login'))
        if user.check_password(form.password.data):
            login_user(user)
            flash('Logged in user: %r' % user.username)
            return redirect(url_for('market.index'))
        else:
            flash('Bad Password')
            return redirect(url_for('.login'))
    return render_template("auth/login.html", login="active", form=form)

@auth.route("/newuser", methods=['GET', 'POST'])
def newuser():
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        user.sent_verification_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        verify_url = url_for('auth.verify_email', token=token,
            _external=True)
        html = render_template('auth/verify_email.html',
            verify_url=verify_url)
        subject = "EggZlist - Please confirm your email"
        send_email(user.email, subject, html)
        login_user(user)
        flash('A verification email has been sent to your mailbox.', 'success')
        return redirect(url_for('market.index'))
    return render_template("auth/newuser.html", login="active", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('market.index'))

@auth.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first()
    items = Item.query.filter_by(user_id=user.id).order_by(Item.post_date.desc()).all()
    if user == None:
        flash('User not found')
        return redirect(url_for('market.index'))
    return render_template("auth/profile.html", profile="active", user=user, items=items)

@auth.route("/profile/settings")
@login_required
def profile_settings():
    user = g.user
    return render_template("auth/settings.html", profile="active", user=user)

@auth.route("/profile/contact_info", methods=['GET', 'POST'])
@login_required
def profile_contact_info():
    user = g.user
    form = ContactInfoForm()
    if form.validate_on_submit():
        user.email = form.email.data
        user.zipcode = form.zipcode.data
        user.viewable = form.viewable.data
        user.street = form.address.data
        user.city = form.city.data
        user.state = form.state.data
        user.phone_number = form.phone.data
        db.session.add(user)
        db.session.commit()
        flash("Contact Info Saved")
        return redirect(url_for(".profile", username=user.username))
    else:
        if user.is_vendor:
            form.name.data = user.username
            form.email.data = user.email
            form.confirm.data = user.email
            form.zipcode.data = user.zipcode
            form.viewable.data = user.viewable
            form.address.data = user.street
            form.city.data = user.city
            form.state.data = user.state
            form.phone.data = user.phone_number
    return render_template("auth/address_form.html", user=user, form=form)

@auth.route("/profile/edit_about", methods=['GET', 'POST'])
@login_required
def edit_about():
    user = g.user
    form = AboutUserForm()
    if form.validate_on_submit():
        user.about = form.about.data
        db.session.add(user)
        db.session.commit()
        flash("Updated About Section")
        return redirect(url_for(".profile", username=user.username))
    else:
        form.about.data = g.user.about
    return render_template("auth/about_form.html", user=user, form=form)
