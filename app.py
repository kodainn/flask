from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user,login_required
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
        if "signup_button" in request.form:
            username = request.form.get("username")
            password = request.form.get("password")
            re_password = request.form.get("re_password")

            exist_user = User.query.filter(User.username == username).all()
            if exist_user:
                signup_existUser_alert_message = "そのユーザ名は既に使われています"
                return render_template("signup.html", signup_alert_message=signup_existUser_alert_message)

            if password == "" and re_password == "":
                signup_blank_alert_message = "パスワードかパスワード(確認用)が空白です"
                return render_template("signup.html", signup_alert_message=signup_blank_alert_message)
            elif password != re_password:
                signup_type_alert_message = "パスワードとパスワード(確認用)が一致しません"
                return render_template("signup.html", signup_alert_message=signup_type_alert_message)
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")
        elif "back_button" in request.form:
            return redirect("/login")

    else:
        return render_template("signup.html")

#ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "login_button" in request.form:
            username = request.form.get("username")
            password = request.form.get("password")

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect("/")
            else:
                login_type_alert_message = "ユーザネームかパスワードが間違っています。"
                return render_template("login.html", login_alert_message=login_type_alert_message)
        elif "signup_button" in request.form:
            return redirect("signup")
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
    app.run(debug=True)