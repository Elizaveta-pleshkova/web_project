import os
import csv

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_sqlalchemy import SQLAlchemy
from data import db_session
from flask_login import LoginManager, UserMixin, login_manager, login_user, login_required, \
    logout_user
import sqlalchemy

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/catalog.db'
db = SQLAlchemy(app)
manager = LoginManager(app)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,
                   primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = db.Column(db.String(256), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer,
                   primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=True)
    autor = db.Column(db.String, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    genre = db.Column(db.String, nullable=True)
    photo = db.Column(db.BLOB, nullable=True)


@app.route('/', methods=['GET'])
def home():
    return render_template('start.html', book=Book.query.all())


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    email = request.form.get('login')
    hashed_password = request.form.get('password')

    if email and hashed_password:
        user = User.query.filter_by(email=email).first()
        if user.hashed_password == hashed_password:
            login_user(user)
            next_page = request.args.get('next')
            redirect(next_page)
        else:
            flash('Login or password is not correct')

    else:
        flash('Please fill login and password fields')
        return render_template('login.html')

    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/forusers', methods=['GET'])
@login_required
def stage():
    return render_template('forusers.html', book=Book.query.all())


@app.route('/register', methods=['POST', 'GET'])
def register():
    email = request.form.get('login')
    hashed_password = request.form.get('password')
    hashed_password2 = request.form.get('password2')

    if request.method == 'post':
        if not (email or hashed_password or hashed_password2):
            flash('Please, fill all fields!')
        elif hashed_password != hashed_password2:
            flash('Password are not equal!')
        else:
            new_user = User(email=email, hashed_password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('/'))


@app.after_request
def redirect_to_signin(responce):
    if responce.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return responce


def main():
    db_session.global_init("db/catalog.db")
    app.secret_key = os.urandom(12)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
