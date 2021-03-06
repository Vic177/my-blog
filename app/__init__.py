from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager 
from flask_pagedown import PageDown
from flask_avatars import Avatars
from flask_dropzone import Dropzone
from flask_ckeditor import CKEditor
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_pjax import  PJAX


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
login_manager = LoginManager()
avatars = Avatars()
dropzone = Dropzone()
ckeditor = CKEditor()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
photosSet = UploadSet('photos', IMAGES)
pjax = PJAX()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    avatars.init_app(app)
    dropzone.init_app(app)
    ckeditor.init_app(app)
    pjax.init_app(app)

    configure_uploads(app, photosSet)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')
    
    return app
