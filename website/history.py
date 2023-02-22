from flask import Blueprint, flash, request, redirect, url_for, render_template
#from flask.globals import request
from .models import User
from . import db
# from flask.templating import render_template, request, flash,# redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import regex as re
from flask_login import login_user, login_required, logout_user, current_user

history_blu = Blueprint('history', __name__)
@login_required
@history_blu.route('/search-history')
def searchhist():
    return render_template("history.html", user=current_user)



