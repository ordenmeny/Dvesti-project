from flask import Flask, render_template, request, url_for, redirect, flash
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c45264839c074e240ec999b2d2d97'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dvesti.db"

app.config['UPLOAD_FOLDER'] = 'static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)

ckeditor = CKEditor(app)


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


class RegistrationDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    mobile_number = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())


@app.route('/')
def index():
    users = db.session.execute(db.select(Article).order_by(Article.date)).scalars()
    return render_template('main/index.html', users=users)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/dashboard.html', title='Dashboard')


@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    form = Add_article()
    if request.method == 'POST' and form.validate():
        title_article = request.form['title_article']
        tag = request.form['tag']
        text_article = request.form['text_article']
        main_img = request.files['main_img']

        # Добавление файла
        if main_img.filename == '':
            app.config['UPLOAD_FOLDER'] = 'static/images/articles'
            filename = 'no-image-v2-500x383@2x.jpg'
            main_img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif main_img:
            app.config['UPLOAD_FOLDER'] = 'static/images/articles'
            filename = secure_filename(main_img.filename)
            filename = str(str(uuid.uuid1()) + '.' + str(filename)[::-1].split('.')[0][::-1])
            main_img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Изображение не добавлено')
            return redirect(url_for("add_article"))

        if len(title_article) == 0 or len(text_article) == 0:
            flash('Не все поля заполнены')
            return redirect(url_for("add_article"))

        article = Article(
            title_article=title_article, tag=tag, text_article=text_article, main_img=filename
        )
        try:
            db.session.add(article)
            db.session.commit()
        except:
            flash('Ошибка добавления в базу данных!')
            return redirect(url_for("add_article"))

        return redirect(url_for("dashboard"))
    return render_template('dashboard/add_article.html', form=form, title='Добавить статью')


@app.route('/registr', methods=['GET', 'POST'])
def registr():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile_number = request.form['mobile_number']

        first_email = RegistrationDB.query.filter_by(email=email).first()

        if name and password and mobile_number and not first_email:
            password_hash = generate_password_hash(password)
            registrDB = RegistrationDB(name=name, email=email, password=password_hash, mobile_number=mobile_number)

            try:
                db.session.add(registrDB)
                db.session.commit()
            except:
                flash('Ошибка добавления в базу данных!')
                return redirect(url_for("registr"))

            flash('Вы зарегистрировались! Дождитесь приглашения по email')
            return redirect(url_for("index"))
        else:
            flash('Поля заполнены неправильно!')

    return render_template('registr.html', title='Регистрация', form=form)


@app.route('/signin')
def signin():
    return render_template('signin.html', title='Войти')


if __name__ == "__main__":
    app.run(debug=True)
