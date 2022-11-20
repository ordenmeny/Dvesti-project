from flask import Flask, render_template, request, url_for, redirect, flash
from wtforms import Form, BooleanField, StringField, validators, SubmitField, TextAreaField, FileField
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import uuid as uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c45264839c074e240ec999b2d2d97'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dvesti.db"

app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)

ckeditor = CKEditor(app)


def my_length_check(form, field):
    if len(field.data) > 50:
        raise validators.ValidationError('Field must be less than 50 characters')


class Add_article(Form):
    title_article = StringField('title_article')
    text_article = CKEditorField('text_article')
    main_img = FileField('Image File')


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_article = db.Column(db.String, nullable=False)
    text_article = db.Column(db.Text, nullable=False)
    main_img = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())


@app.route('/')
def index():
    return render_template('main/index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/dashboard.html', title='Dashboard')


@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    form = Add_article()
    if request.method == 'POST' and form.validate():
        title_article = request.form['title_article']
        text_article = request.form['text_article']
        main_img = request.files['main_img']

        # Grab Image Name
        pic_filename = secure_filename(main_img.filename)

        # set UUID
        pic_name = str(uuid.uuid1()) + '_.' + pic_filename

        # Save That image
        main_img.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        # name picture to add to DB
        main_img = pic_name

        if len(title_article) == 0 or len(text_article) == 0:
            flash('Не все поля заполнены')
            return redirect(url_for("add_article"))
        article = Article(
            title_article=title_article, text_article=text_article, main_img=main_img
        )

        try:
            db.session.add(article)
            db.session.commit()
        except:
            flash('Ошибка!')
            return redirect(url_for("add_article"))

        return redirect(url_for("dashboard"))
    return render_template('dashboard/add_article.html', form=form, title='Добавить статью')


if __name__ == "__main__":
    app.run(debug=True)
