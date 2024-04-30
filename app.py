from flask import Flask,redirect,url_for,render_template, request,session,flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)


db = SQLAlchemy(app)
migrate = Migrate(app, db) 

class Message(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    password_hash = db.Column("password_hash", db.String(100))
    messages = db.relationship("Message", backref="user", lazy=True)

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

@app.route("/send_message", methods=["POST"])
def send_message():
    if "user" in session:
        user = session["user"]
        content = request.form["content"]
        user_obj = Users.query.filter_by(name=user).first()
        message = Message(user_id=user_obj.id, content=content)
        db.session.add(message)
        db.session.commit()
        print("Сообщение успешно добавлено:", message)
        flash("Сообщение отправлено!")
        return redirect(url_for("user"))
    else:
        flash("Вы не вошли в систему")
        return redirect(url_for("login"))

@app.route("/register", methods=["POST", "GET"])
def register():
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
    



@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    messages = None
    
    if "user" in session:
        user = session["user"]
        
        if request.method == "POST":
            content = request.form.get("content")
            if content:
                user_obj = Users.query.filter_by(name=user).first()
                message = Message(user_id=user_obj._id, content=content) 
                db.session.add(message)
                db.session.commit()
                flash("Сообщение отправлено")
        messages = Message.query.all()           
    else:
        flash("Вы не вошли в систему")
        return redirect(url_for("login"))
    
    return render_template("user.html", email=email, messages=messages)


@app.route("/logout")
def logout():
    flash("Вы вышли из системы!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)   
