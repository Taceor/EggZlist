# -*- coding: utf-8 -*-
import datetime
import os
import sys
from app import models
from app.token import generate_confirmation_token, confirm_token
from app.email import send_email, mail
from app.login_manager import lm
from sqlalchemy import asc, desc
from flask import Blueprint, redirect, url_for, current_app, request,\
                  flash, render_template, g, session, send_from_directory,\
                  jsonify
from config import SECRET_KEY
from app.models import Item, User, Photo, db
from app.forms import ContactInfoForm, ItemInfoForm, LoginForm, NewUserForm,\
                  AboutUserForm, ListingPhotosForm, SearchForm
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from werkzeug import secure_filename

market = Blueprint('market', __name__)

@market.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@market.route("/")
@market.route("/index")
def index():
    item = Item.query.first()
    return render_template("index.html", item=item, home="active")

@market.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    user = g.user
    form = ContactInfoForm()
    if form.validate_on_submit() and user.is_authenticated:
        user.zipcode=form.zipcode.data
        user.viewable=form.viewable.data
        user.street=form.address.data
        user.city=form.city.data
        user.state=form.state.data
        user.phone_number=form.phone.data
        user.is_vendor = True
        db.session.add(user)
        db.session.commit()
        flash("Account updated")
        return redirect(url_for(".sell_2", user_id=user.id))
    else:
        form.name.data = user.username
        form.email.data = user.email
        form.confirm.data = user.email
        form.zipcode.data = user.zipcode
        if user.viewable:
            form.viewable.data = True
        if user.street:
            form.address.data = user.street
        if user.city:
            form.city.data = user.city
        if user.state:
            form.state.data = user.state
        if user.phone_number:
            form.phone.data = user.phone_number
    return render_template("market/sell.html", form=form, sell="active", info="rectangle")

@market.route("/sell_2/", methods=['GET', 'POST'])
@login_required
def sell_2():
    form = ItemInfoForm()
    user = g.user
    if form.validate_on_submit():
        item = Item(form.title.data, form.category.data, form.price.data,
                    form.price_type.data, form.description.data,
                    user_id=user.id)
        db.session.add(item)
        db.session.commit()
        flash("Item created")
        return redirect(url_for(".upload", item_id=item.id))
    return render_template("market/sell_2.html", form=form, sell="active", items="rectangle")

@market.route("/upload/<item_id>", methods=['GET', 'POST'])
@login_required
def upload(item_id):
    form = ListingPhotosForm(request.form)
    user = g.user
    item = Item.query.get(item_id)
    if form.add_photo.data:
        form.photos.append_entry()
        """
        if request.files:
            request.form = request.form.copy()
            request.form.update(request.files)
        """
    elif request.form and form.validate_on_submit():
        i = 0
        for entry in form.photos.entries:
            if entry.photo_file:
                input_name = entry.photo_file.name
                file = request.files[input_name]
                ext = os.path.splitext(file.filename)[1]
                print >> sys.stderr, str(ext)
                if ext not in current_app.config['ALLOWED_EXTENSIONS']:
                    print >> sys.stderr, "not allowed or none"
                    continue
                filename = str(item.id) + "_" + str(i) + str(ext)
                print >> sys.stderr, str(filename)
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                print >> sys.stderr, str(full_path)
                file.save(full_path)
                photo_path = filename
                p = Photo(item.id, photo_path, full_path)
                db.session.add(p)
                db.session.commit()        
                i+=1
        return redirect(url_for(".listing", item_id=item.id))
    return render_template("market/upload.html", form=form, sell="active", item=item)

@market.route("/edit/<item_id>", methods=['GET', 'POST'])
@login_required
def edit(item_id):
    user = g.user
    item = Item.query.get(item_id)
    form = ItemInfoForm(obj=item)
    if form.validate_on_submit():
        item.title = form.title.data
        item.category = form.category.data
        item.price = form.price.data
        item.price_type = form.price_type.data
        item.description = form.description.data
        db.session.add(item)
        db.session.commit()
        flash("Item updated")
        return redirect(url_for(".listing", item_id=item.id))
    else:
        if user.is_authenticated and user.id == item.user_id:
            form.title.data = item.title
            form.category.data = item.category
            form.price.data = item.price
            form.price_type.data = item.price_type
            form.description.data = item.description
        else:
            flash("Wrong User")
            return redirect(url_for(".listing", item_id=item.id))
    return render_template("market/sell_2.html", form=form, sell="active", items="rectangle")

@market.route("/_delete_listing/<item_id>")
@login_required
def delete_listing(item_id):
    user = g.user
    item = Item.query.get(item_id)
    if item is not None:
        if user.id == item.user_id:
            db.session.delete(item)
            db.session.commit()
            flash("Listing for " + item.title + " deleted")
        else:
            flash("Wrong User")
    else:
        flash("No such item")
    return redirect(url_for('auth.profile', username=g.user.username))

@market.route("/_flag_item")
def flag_item():
    item_id = request.args.get('item_id')
    user_id = request.args.get('user_id')
    item = Item.query.get(item_id)
    if item is not None:
        item.flags = Item.flags + 1 
        """Avoiding "race conditions"
        See: http://stackoverflow.com/questions
        /2334824/how-to-increase-a-counter-in-sqlalchemy
        """
        db.session.add(item)
        db.session.commit()
        worked=True
    return jsonify(worked=worked)

@market.route("/_save_item")
def save_item():
    item_id = request.args.get('item_id')
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    item = Item.query.get(item_id)
    if user is not None and item is not None:
        user.saves.append(item)
        db.session.commit()
        worked=True
    return jsonify(worked=worked)

@market.route("/buy", methods=['GET', 'POST'])
def buy():
    form = SearchForm()
    if form.validate_on_submit():
        items = Item.query.whoosh_search(form.query.data).all()
    else:
        items = Item.query.order_by(Item.post_date.desc()).all()
    return render_template("market/buy.html", buy="active", items=items, form=form)

@market.route("/_markmap")
def markmap():
    swlat = request.args.get('swlat')
    swlng = request.args.get('swlng')
    nelat = request.args.get('nelat')
    nelng = request.args.get('nelng')
    users = User.query.all()
    markers = []
    local_users = []
    for user in users:
        if float(swlat) < user.lat < float(nelat) and \
           float(swlng) < user.lng < float(nelng) and \
           user.viewable:
            local_users.append({ 'name':user.username, 'lat':user.lat, 'lng':user.lng})
    return jsonify(local_users=local_users)

@market.route("/listing/<item_id>")
def listing(item_id):
    item = Item.query.get(item_id)
    if item is not None:
        delta = datetime.datetime.today() - item.post_date
        return render_template("market/listing.html", buy="active", item=item, days=delta.days)
    else:
        flash("Item doesn't exist")
        return redirect(url_for('.buy'))

@market.route("/_set_user_latlng")
def set_user_latlng():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    listing_id = request.args.get('listing_id')
    user = Item.query.get(listing_id).user
    user.lat = lat
    user.lng = lng
    db.session.add(user)
    db.session.commit()
    data = { 'username':user.username, 'lat':lat, 'lng':lng }
    return jsonify(data=data)

@market.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
