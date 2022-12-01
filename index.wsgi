import os
import sys
sys.path.append('/home/c/cc47201/newsite/public_html/venv/lib/python3.6/site-packages/')
from flask import Flask
from wtforms import Form, BooleanField, StringField, validators, SubmitField, TextAreaField, FileField, PasswordField, \
    EmailField
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_manager, login_required, logout_user, current_user
import smtplib
from email.mime.text import MIMEText
app = Flask(__name__)
application = app

app.config['SECRET_KEY'] = 'c45264839c074e240ec999b2d2d97'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dvesti.db"
app.config['UPLOAD_FOLDER'] = 'static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}


ckeditor = CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message = "Доступ запрещен. В данный момент у вас нет доступа к этой странице."

class Add_article(Form):
    title_article = StringField('title_article')
    text_article = CKEditorField('text_article')
    tag = StringField('tag')
    main_img = FileField('Image File')


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_article = db.Column(db.String, nullable=False)
    tag = db.Column(db.String, nullable=False)
    text_article = db.Column(db.Text, nullable=False)
    main_img = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())


class RegistrationForm(Form):
    name = StringField('Username')
    email = EmailField('Email Address')
    password = PasswordField('Password')
    mobile_number = StringField('mobile number')


class LoginForm(Form):
    email = EmailField('Email Address')
    password = PasswordField('Password')


class RegistrationDB(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    mobile_number = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())


class TempRegistrDB(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    mobile_number = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())



if __name__ == '__main__':
    app.run()