# -*- coding: utf-8 -*-
import datetime
import os
import sys
from app import app, db, models, lm, mail
from app.token import generate_confirmation_token, confirm_token
from app.email import send_email
from sqlalchemy import asc, desc
from flask import Blueprint, redirect, url_for, current_app, request,\
                  flash, render_template, g, session, send_from_directory,\
                  jsonify
from config import SECRET_KEY
from models import Item, User, Photo
from forms import ContactInfoForm, ItemInfoForm, LoginForm, NewUserForm,\
                  AboutUserForm, ListingPhotosForm
from flask.ext.login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from werkzeug import secure_filename

@app.route('/verify/<token>')
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
    return redirect(url_for('profile', username = user.username)) 

@app.route('/resend')
@login_required
def resend_verification():
    td = datetime.datetime.now() - g.user.sent_verification_on
    if g.user.sent_verification_on is None or \
       td > datetime.timedelta(seconds=3600):
        token = generate_confirmation_token(g.user.email)
        verify_url = url_for('verify_email', token=token, _external=True)
        html = render_template('profile/verify_email.html', verify_url=verify_url)
        subject = "EggZlist - Please verify your email"
        send_email(g.user.email, subject, html)
        flash('A new verification email has been sent.', 'success')
        g.user.sent_verification_on = datetime.datetime.now()
        db.session.add(g.user)
        db.session.commit()
    else:
        flash("Verification email already sent. Please wait a few minutes \
        before requesting another.")
    return redirect(url_for('profile', username = g.user.username))

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user==None:
            flash ('No such user')
            return redirect(url_for('login'))
        if user.check_password(form.password.data):
            login_user(user)
            flash('Logged in user: %r' % user.username)
            return redirect(url_for('index'))
        else:
            flash('Bad Password')
            return redirect(url_for('login'))
    return render_template("login/login.html", login="active", form=form)

@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        user.sent_verification_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        verify_url = url_for('verify_email', token=token,
            _external=True)
        html = render_template('profile/verify_email.html',
            verify_url=verify_url)
        subject = "EggZlist - Please confirm your email"
        send_email(user.email, subject, html)
        login_user(user)
        flash('A verification email has been sent to your mailbox.', 'success')
        return redirect(url_for('index'))
    return render_template("login/newuser.html", login="active", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first()
    items = Item.query.filter_by(user_id=user.id).order_by(Item.post_date.desc()).all()
    if user == None:
        flash('User not found')
        return redirect(url_for('index'))
    return render_template("profile/profile.html", profile="active", user=user, items=items)

@app.route("/profile/settings")
@login_required
def profile_settings():
    user = g.user
    return render_template("profile/settings.html", profile="active", user=user)

@app.route("/profile/contact_info", methods=['GET', 'POST'])
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
        return redirect(url_for("profile", username=user.username))
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
    return render_template("profile/address_form.html", user=user, form=form)

@app.route("/profile/edit_about", methods=['GET', 'POST'])
@login_required
def edit_about():
    user = g.user
    form = AboutUserForm()
    if form.validate_on_submit():
        user.about = form.about.data
        db.session.add(user)
        db.session.commit()
        flash("Updated About Section")
        return redirect(url_for("profile", username=user.username))
    else:
        form.about.data = g.user.about
    return render_template("profile/about_form.html", user=user, form=form)

@app.route("/")
@app.route("/index")
def index():
    item = Item.query.first()
    return render_template("index.html", item=item, home="active")

@app.route('/sell', methods=['GET', 'POST'])
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
        return redirect(url_for("sell_2", user_id=user.id))
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
    return render_template("sell/sell.html", form=form, sell="active", info="rectangle")

@app.route("/sell_2/", methods=['GET', 'POST'])
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
        return redirect(url_for("upload", item_id=item.id))
    return render_template("sell/sell_2.html", form=form, sell="active", items="rectangle")

@app.route("/upload/<item_id>", methods=['GET', 'POST'])
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
                if ext not in app.config['ALLOWED_EXTENSIONS']:
                    print >> sys.stderr, "not allowed or none"
                    continue
                filename = str(item.id) + "_" + str(i) + str(ext)
                print >> sys.stderr, str(filename)
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print >> sys.stderr, str(full_path)
                file.save(full_path)
                photo_path = filename
                p = Photo(item.id, photo_path, full_path)
                db.session.add(p)
                db.session.commit()        
                i+=1
        return redirect(url_for("listing", item_id=item.id))
    return render_template("sell/upload.html", form=form, sell="active", item=item)

@app.route("/edit/<item_id>", methods=['GET', 'POST'])
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
        return redirect(url_for("listing", item_id=item.id))
    else:
        if user.is_authenticated and user.id == item.user_id:
            form.title.data = item.title
            form.category.data = item.category
            form.price.data = item.price
            form.price_type.data = item.price_type
            form.description.data = item.description
        else:
            flash("Wrong User")
            return redirect(url_for("listing", item_id=item.id))
    return render_template("sell/sell_2.html", form=form, sell="active", items="rectangle")

@app.route("/_delete_listing/<item_id>")
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
    return redirect(url_for('profile', username=g.user.username))

@app.route("/_flag_item")
def flag_item():
    item_id = request.args.get('item_id')
    user_id = request.args.get('user_id')
    if user_id is not -1:
        user = User.query.get(user_id)
    else:
        pass
        #TODO: Anonymous user reports
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

@app.route("/_save_item")
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

@app.route("/buy")
@app.route("/buy/<filter_type>")
def buy(filter_type=None):
    if filter_type is not None:
        if filter_type == "dairy" or filter_type == "Dairy":
            items = Item.query.filter_by(category="Dairy").order_by(Item.post_date.desc()).all()
        elif filter_type == "protein" or filter_type == "Protein":
            items = Item.query.filter_by(category="Protein").order_by(Item.post_date.desc()).all()
        elif filter_type == "vegetable" or filter_type == "Vegetable":
            items = Item.query.filter_by(category="Vegetable").order_by(Item.post_date.desc()).all()
        elif filter_type == "fruit" or filter_type == "Fruit":
            items = Item.query.filter_by(category="Fruit").order_by(Item.post_date.desc()).all()
        elif filter_type == "grain" or filter_type == "Grain":
            items = Item.query.filter_by(category="Grain").order_by(Item.post_date.desc()).all()
        elif filter_type == "other" or filter_type == "Other":
            items = Item.query.filter_by(category="Other").order_by(Item.post_date.desc()).all()
        else:
            flash("Error: Bad Filter")
            items = Item.query.order_by(Item.post_date.desc()).all()
    else:
        items = Item.query.order_by(Item.post_date.desc()).all()
    return render_template("buy/buy.html", buy="active", items=items)

@app.route("/_markmap")
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

@app.route("/listing/<item_id>")
def listing(item_id):
    if item_id is not None:
        item = Item.query.get(item_id)
        delta = datetime.datetime.today() - item.post_date
        return render_template("buy/listing.html", buy="active", item=item, days=delta.days)
    else:
        flash("Item doesn't exist")
        return redirect(url_for('buy'))

@app.route("/_set_user_latlng")
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

@app.route("/community")
def community():
    return render_template('community/community.html', community="active")

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
