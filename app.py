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
from flask_login import LoginManager, UserMixin, login_user, login_manager, login_required, logout_user, current_user
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c45264839c074e240ec999b2d2d97'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dvesti.db"

app.config['UPLOAD_FOLDER'] = 'static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)

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


@login_manager.user_loader
def load_user(user_id):
    return RegistrationDB.query.get(int(user_id))


@app.route('/')
def index():
    users = db.session.execute(db.select(Article).order_by(Article.date)).scalars()
    return render_template('main/index.html', users=users, title='Д-вести: статьи и новости')


@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('add_article'))
    # return render_template('dashboard/dashboard.html', title='Dashboard')


@app.route('/add_article', methods=['GET', 'POST'])
@login_required
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
            filename = 'no-img.png'
            # main_img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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

        flash('Статья добавлена!')
        return redirect(url_for("index"))
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
            tempregistrDB = TempRegistrDB(name=name, email=email, password=password_hash, mobile_number=mobile_number)

            try:
                db.session.add(tempregistrDB)
                db.session.commit()
            except:
                flash('Ошибка добавления в базу данных!')
                return redirect(url_for("registr"))

            flash('Вы зарегистрировались! Дождитесь приглашения по email (письмо может лежать в спам)')
            return redirect(url_for("index"))
        else:
            flash('Поля заполнены неправильно! Или такой аккаунт уже существует!')

    return render_template('registr.html', title='Регистрация', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        email = request.form['email']
        password = request.form['password']

        if email and password:
            user = db.session.execute(
                db.select(RegistrationDB).filter_by(email=email)).first()  # select raw with input email(iter) or None

            if user:
                password_hash = user[0].password
                check_password = check_password_hash(password_hash, password)

                if check_password:
                    user_log = user[0]
                    login_user(user_log)
                    text = f'Вы вошли под логином {email}'
                    flash(text)
                    return redirect(url_for("dashboard"))
                else:
                    flash('Неверный пароль')
                    return redirect(url_for("signin"))

            else:
                flash('Такого пользователя не существует')
                return redirect(url_for("signin"))
        else:
            flash('Введите данные')
            return redirect(url_for("signin"))

    return render_template('signin.html', title='Войти', form=form)


def send_email(message, receiver):
    sender = 'newsmobileads@gmail.com'
    password = 'zsvuepxgypsmaypn'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    try:
        server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = "Школьная газета dvesti"
        server.sendmail(sender, receiver, msg.as_string())
        return 'Сообщение отправлено'
    except:
        return 'Произошла ошибка!'


@app.route('/receive/')
@app.route('/receive/<int:id>/<check>')
def receive(id=None, check=None):
    users = db.session.execute(db.select(TempRegistrDB)).scalars().all()
    print(users)
    if check == 'success':
        get_user = db.get_or_404(TempRegistrDB, id)
        name = get_user.name
        email = get_user.email
        password = get_user.password
        mobile_number = get_user.mobile_number
        date = get_user.date

        user_reg_db = RegistrationDB(name=name, email=email, password=password, mobile_number=mobile_number, date=date)

        try:
            db.session.delete(get_user)
            db.session.add(user_reg_db)
            db.session.commit()
            # send message to email
            message = 'Вы были зарегистрированы на сайте школьной газеты dvesti.\nТеперь вы можете войти в Кабинет Редактора!'
            send_email(message=message, receiver=email)
        except:
            flash('Ошибка добавления в базу данных редакторов!')
            return redirect(url_for("registr"))

        return redirect(url_for('receive'))

    return render_template('dashboard/receive.html', title='Админ панель', users=users)


@app.route('/show_article/<int:id>', methods=['GET', 'POST'])
def show_article(id=None):
    post = db.get_or_404(Article, id)
    title = post.title_article
    tag = post.tag
    text_article = post.text_article
    main_img = post.main_img
    return render_template('main/show_article.html', title=title, tag=tag, text_article=text_article, main_img=main_img)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))


if __name__ == "__main__":
    app.run(debug=True)
