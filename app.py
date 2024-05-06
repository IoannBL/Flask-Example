from flask import Flask,redirect,url_for,render_template, request,session,flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.permanent_session_lifetime = timedelta(minutes=5)


db = SQLAlchemy(app)
migrate = Migrate(app, db) 

class Message(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
 
class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    password_hash = db.Column("password_hash", db.String(100))
    messages = db.relationship("Message", backref="user", lazy=True, foreign_keys=[Message.user_id])
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)

        
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/view")
def view():
    return render_template("view.html", values=Users.query.all())


@app.route("/user", methods=["POST", "GET"])
def user():
    """Отображает страницу пользователя. Обрабатывает сообщения общего чата. Выводит уведомления"""
    email = None
    messages = None
    users = Users.query.all()
    if "user" in session:
        user = session["user"]
        user_obj = Users.query.filter_by(name=user).first()
        email = user_obj.email
        
        if request.method == "POST":
            content = request.form.get("content")
            if content:
                user_obj = Users.query.filter_by(name=user).first()
                message = Message(user_id=user_obj._id, content=content, recipient_id="all" ) 
                db.session.add(message)
                db.session.commit()
                flash("Сообщение отправлено")
        messages = Message.query.filter_by(recipient_id="all").all()           
    else:
        flash("Вы не вошли в систему")
        return redirect(url_for("login"))
    
    return render_template("user.html", email=email, user_name=user, messages=messages,users=users)


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    """Отображает профиля пользователей. Обрабатывает личные сообщения пользователей. Выводит уведомления"""
    user_name = session.get("user") 

    if not user_name:
        flash("Вы не вошли в систему", "error")
        return redirect(url_for("home"))
    
    user_obj = Users.query.filter_by(name=user_name).first()
    recipient = Users.query.filter_by(name=username).first()

    if not recipient:
        flash("Пользователь не найден", "error")
        return redirect(url_for("home"))
    
    email = recipient.email
    email_us = user_obj.email
    messages = Message.query.filter(
        ((Message.user_id == user_obj._id) & (Message.recipient_id == recipient._id)) |
        ((Message.user_id == recipient._id) & (Message.recipient_id == user_obj._id))).all()
    
    if request.method == "POST":
        content = request.form.get("content")
    
        if content:
            message = Message(user_id=user_obj._id, content=content, recipient_id=recipient._id) 
            db.session.add(message)
            db.session.commit()
            flash("Сообщение отправлено пользователю " + username)
            return redirect(url_for("profile", username=username))
    
    return render_template("user_profile_list.html", username=username, messages=messages, user=user_name, email=email, email_us = email_us )
   

@app.route("/register", methods=["POST", "GET"])
def register():
    """Обрабатывает процесс регистрации пользователя. POST - получает данные формы (имя, email, пароль), создает нового пользователя в базе данных. 
    GET - отображает страницу регистрации. Выводит уведомления"""
    if request.method == "POST":
        name = request.form["nm"]
        email = request.form["email"]
        password = request.form["password"]

        user = Users(name=name, email=email, password=password,)
        db.session.add(user)
        db.session.commit()
        flash("Регистрация прошла успешно!")
        return redirect(url_for("login"))
    else:
        return render_template("register.html")
    

@app.route("/login", methods=["POST", "GET"])
def login():
    """Обрабатывает процесс входа пользователя. POST - получает данные формы и сверяет их с данными из базы. GET - отображает страницу входа. Выводит уведомления"""
    if "user" in session:
        flash("Вход уже выполнен")
        return redirect(url_for("user"))
    
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        password = request.form["password"]
        
        found_user = Users.query.filter_by(name=user).first()
        if found_user:
            if check_password_hash(found_user.password_hash, password):
                session["user"] = user
                session["email"] = found_user.email
                flash(f"Добро пожаловать, {user}!")
                return redirect(url_for("user"))
        
        flash("Неверное имя пользователя или пароль", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Обрабатывает процесс выхода пользователя из системы. Удаляет сессионные переменные пользователя и выводит уведомление о выходе из системы."""
    flash("Вы вышли из системы!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))
   

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)   
