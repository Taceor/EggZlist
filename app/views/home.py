# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, url_for, current_app, request,\
                  flash, render_template, g, session, send_from_directory

home = Blueprint('home', __name__)

@home.route("/")
@home.route("/index")
@home.route("/home")
def index():
   return render_template("home/index.html", home="active")
