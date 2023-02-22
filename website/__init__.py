from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'fateh muhammad sani '
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .product import product
    from .results import results_blu
    from .history import history_blu
    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(product,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/')
    #app.register_blueprint(results,url_prefix='/')
    app.register_blueprint(results_blu,url_prefix='/')
    app.register_blueprint(history_blu,url_prefix='/')
    #from .models import User, Note 
    from .models import User, Note
    #create_database(app)
    with app.app_context():
        db.create_all()
    #from . import models
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app


#def create_database(app):
#    if not path.exists('webiste/' + DB_NAME):
#        db.create_all(app=app)
#        print('Created Database!')