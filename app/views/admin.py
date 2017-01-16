# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, url_for, current_app, request,\
                  flash, render_template, g, session, send_from_directory
from app.models import db, Item, User, Photo
from app.login_manager import lm
from flask_login import login_required, login_user, logout_user, current_user

admin = Blueprint('admin', __name__)

def redirect_url(default='home.index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

@admin.route("/portal")
@login_required
def portal():
    user = g.user
    if user.is_admin:
        flagged_items = Item.query.filter(Item.flags != 0).all()
        return render_template("admin/portal.html", flagged_items=flagged_items)
    else:
        return render_template("market/buy.html")

@admin.route("/inspect/<int:item_id>")
@login_required
def inspect(item_id):
    user = g.user
    if user.is_admin:
        item = Item.query.get(item_id)
        if item == None:
            return redirect(redirect_url())
        else:
            return render_template("admin/inspect.html", item=item)
    else:
        return redirect(redirect_url())
@admin.route("/delete/<int:item_id>")
@login_required
def delete(item_id):
    user = g.user
    if user.is_admin:
        item = Item.query.get(item_id)
        if item == None:
            return redirect(redirect_url())
        else:
            db.session.delete(item)
            db.session.commit()
            flash("Deleted post " + str(item.id) +".")
            return redirect(url_for('.portal'))
    else:
        return redirect(redirect_url())
