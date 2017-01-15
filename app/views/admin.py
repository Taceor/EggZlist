# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, url_for, current_app, request,\
                  flash, render_template, g, session, send_from_directory
from app.models import db, Item, User, Photo
from app.login_manager import lm
from flask_login import login_required, login_user, logout_user, current_user

admin = Blueprint('admin', __name__)


@admin.route("/portal")
@login_required
def portal():
    user = g.user
    if user.is_admin:
        flagged_items = Item.query.filter(Item.flags != 0).all()
        return render_template("admin/portal.html", flagged_items=flagged_items)
    else:
        return render_template("market/buy.html")
