# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, url_for, current_app, request,\
                  flash, render_template, g, session, send_from_directory,\
                  jsonify

comm = Blueprint('comm', __name__)

@comm.route("/community")
def community():
    return render_template("community/community.html", community="active")
