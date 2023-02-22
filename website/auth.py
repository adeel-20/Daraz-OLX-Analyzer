from flask import Blueprint, flash, request, redirect, url_for, render_template
#from flask.globals import request
from .models import User
from . import db
# from flask.templating import render_template, request, flash,# redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import regex as re
from flask_login import login_user, login_required, logout_user, current_user

# python code to check valadity of email address
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def checkmail(email):
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False


def password_check(passwd):

    SpecialSym = ['$', '@', '#', '%']
    #val = True

    if len(passwd) < 6:
        return('Length of password should be at least 6 characters')
        #val = False

    if len(passwd) > 20:
        return('Length of password should not be greater than 8 characters')
        #val = False

    if not any(char.isdigit() for char in passwd):
        return('Password should have at least one numeral')
        #val = False

    if not any(char.isupper() for char in passwd):
        return('Password should have at least one uppercase letter')
        #val = False

    if not any(char.islower() for char in passwd):
        return('Password should have at least one lowercase letter')
        #val = False

    if not any(char in SpecialSym for char in passwd):
        return('Password should have at least one of the symbols $@#')
        #val = False
    return 'Tru'


# email checker ends here
auth = Blueprint('auth', __name__)



#def login():
# #   data = request.form
#  #  print(data)
#    return render_template("login.html", text="Use this to show data from python")
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)
#def login():
#    if request.method == 'POST':
#        email = request.form.get('email')
#        password = request.form.get('password')
#
#        user = User.query.filter_by(email=email).first()
#        if user:
#            if check_password_hash(user.password, password):
#                flash('Logged in successfully!', category='success')
#                login_user(user, remember=True)
#                return redirect(url_for('views.home'))
#            else:
#                flash('Incorrect password, try again.', category='error')
#        else:
#            flash('Account does not exist.', category='error')
#
#    return render_template("login.html",boolean=True)

#@auth.route('/login', methods=['GET', 'POST'])
#def login():
   # if request.method == 'POST':
   #     email = request.form.get('email')
   #     password = request.form.get('password')
#
   #     user = User.query.filter_by(email=email).first()
   #     if user:
   #         if check_password_hash(user.password, password):
   #             flash('Logged in successfully!', category='success')
   #             #login_user(user, remember=True)
   #             return redirect(url_for('views.home'))
   #         else:
   #             flash('Incorrect password, try again.', category='error')
   #     else:
   #         flash('Email does not exist.', category='error')

  #  return render_template("login.html")



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("sign_out.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        if checkmail(email) == False:
            flash('Please enter a valid email.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif password_check(password1) != 'Tru':
            flash(password_check(password1), category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            
            #login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html",user=current_user)