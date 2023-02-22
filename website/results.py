from flask import Blueprint, flash, request, redirect, url_for, render_template
#from flask.globals import request
#from .models import User
from . import db
import regex as re
from os import name

results_blu = Blueprint('results', __name__)

@results_blu.route('/results')
def results():
   return render_template("res.html",heading=request.args.get('heading'))