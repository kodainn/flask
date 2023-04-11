from flask import Flask, jsonify
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import os
from database import db, Post, User

app = Flask(__name__, static_folder='static')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SECRET_KEY"] = os.urandom(24)
app.config['JSON_AS_ASCII'] = False
db.init_app(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#投稿掲載ページ
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        posts = Post.query.all()
        return render_template("index.html", posts = posts)

#新規登録
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("signup.html")

#ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect("/")
        else:
            alert_message = "そのユーザネームとパスワードは間違っています。"
            return render_template("login.html", alert_message=alert_message)
    else:
        return render_template("login.html")

#ログアウト
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

#投稿を新規作成
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")

        post = Post(title=title, body=body)

        db.session.add(post)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("create.html")

#投稿を編集
@app.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == "GET":
        return render_template("update.html", post=post)
    else:
        post.title = request.form.get("title")
        post.body = request.form.get("body")
        db.session.commit()
        return redirect("/")

#投稿を削除
@app.route("/<int:id>/delete", methods=["GET"])
@login_required
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run()