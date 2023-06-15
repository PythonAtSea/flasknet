from flask import Flask, render_template, flash, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
import logging
from logging.handlers import SMTPHandler


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view="login"
posts=[
    {"author": "Fred", "body" :"Hi buds"},
    {"author": "Sally", "body" :"why"},
]
from models import User, Post
from forms import LoginForm, RegistrationForm, EditForm


if True:
    print("huhwrih")
    if app.config["MAIL_SERVER"]:
        auth = None
        if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
            auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        secure = None
        if app.config["MAIL_USE_TLS"]:
            secure=()
        mail_handler = SMTPHandler(
            mailhost =(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr="pythonatsea@gmail.com",
            toaddrs=app.config["ADMINS"], subject="Flasknet Error",
            credential=auth, secure=secure
        )
        mail_handler.setLevel(logging.INFO)
        print(mail_handler)
        app.logger.addHandler(mail_handler)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("feed"))
    return render_template("index.html")
@app.route("/feed")
@login_required
def feed():
    posts=[
        {"author": "Fred", "body" :"Hi buds"},
        {"author": "Sally", "body" :"why"},
    ]
    return render_template("feed.html", posts=posts)
@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid Username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        flash("You have logged in.")
        return redirect(url_for("index"))
    return render_template("login.html", form=form, title="Login")
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(username=form.username.data, email=form.email.data)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
    return render_template("signup.html", form=form)

@app.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {"author": user, "body": "test #1"},
        {"author": user, "body": "test #2"},
    ]
    return render_template("user.html", user=user, posts=posts)

@app.route("/edit", methods=["GET","POST"])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about = form.about.data
        db.session.commit()
        return redirect(url_for("user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about.data = current_user.about
    return render_template("edit_account.html", form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html")
