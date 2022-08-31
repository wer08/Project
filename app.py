from asyncore import read
from crypt import methods
from time import strftime
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_session import Session
from passlib.hash import sha256_crypt
from datetime import date
import sqlite3
from flask_mail import Mail,Message
from werkzeug.utils import secure_filename

app = Flask(__name__)
#Create Database
#initialize db
con = sqlite3.connect("airplane_reservation.db", check_same_thread=False)
db = con.cursor()
#Create Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/"
Session(app)
#flag to check if succesful registration
flag = -2


app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '1d1815f802c68f'
app.config['MAIL_PASSWORD'] = '13b217b9a01d7d'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


@app.route("/",methods=["GET","POST"])
def index():
    today = date.today()
    d = today.strftime("%Y-%m-%d")
    if request.method == "POST":
        date_depart = request.form.get("date-of-departure")
        print(date_depart)
        return render_template("index.html",d=d)
    else:
        return render_template("index.html",d=d)
    

@app.route("/profil",methods=["GET","POST"])
def profil():
    if request.method == "GET":
        users= db.execute("SELECT * FROM users WHERE username = ?",(session["name"],))
        user = users.fetchone()
        print(user)
        username = user[1]
        name = user[2]
        surname = user[3]
        email = user[4]
        return render_template("profil.html",username=username,name=name,surname=surname,email=email)
    else:
        username = request.form.get("username")
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        users = db.execute("SELECT username, email FROM users WHERE NOT username = ?",(session["name"],))
        for user in users:
            if user[0] == username or user[1] == email:
                flash('There is user with this username or email')
                return redirect("/profil")
        db.execute("UPDATE users SET username = ? , name = ? , surname = ? , email = ? WHERE username = ?",[username,name,surname,email,session["name"]])
        con.commit()
        flash('You changed personal information')
        session["name"] = username
        print(session["name"])
        return render_template("profil.html",username=username,name=name,surname=surname,email=email,flag=flag)
        


@app.route("/logout")
def logout():
    flash('You are logout')
    session["name"] = None
    return redirect("/")

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("inputUsername")
        print(username)
        password = request.form.get("inputPassword")
        users = db.execute("SELECT username FROM users")
        for user in users:
            if username == user[0]:
                passwords = db.execute("SELECT hashed_password FROM users WHERE username = ?",user)
                for hash in passwords:
                    if sha256_crypt.verify(password,hash[0]):
                        flash('You were successfully logged in')
                        session["name"] = username
                        return redirect("/")
                    else:
                        flash('Wrong password')
                        return redirect("/login")
        else:
            flash('Wrong username')
            return redirect("/login")


@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "GET":
        return render_template("profil.html")
    else:
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(app.config["UPLOAD_FOLDER"] + filename)
        picture = app.config["UPLOAD_FOLDER"] + filename
        flash("profile picture changed")
        return redirect("/profil")




@app.route("/register", methods=["GET","POST"]) 
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("inputUsername")
        name = request.form.get("inputName")
        surname = request.form.get("inputSurname")
        email = request.form.get("inputEmail")
        password = request.form.get("inputPassword")
        confirm = request.form.get("inputConfirmPassword")
        if not password == confirm:
            flash("Password and confirmation are not the same")
            return redirect("/register")
        else:
            users = db.execute("SELECT username,email FROM users")
            for user in users:
                if username == user[0] or email == user[1]:
                    flash("This username or email is taken")
                    return redirect("/register")
            hash_password = sha256_crypt.hash(password)
            db.execute("INSERT INTO users (username,name,surname,email,hashed_password) VALUES (?,?,?,?,?)",(username,name,surname,email,hash_password))
            con.commit()
            msg = Message('Registration confirmation', sender =   'peter@mailtrap.io', recipients = ['paul@mailtrap.io'])
            msg.body = "You are registered"
            mail.send(msg)
            flash("Registration succesful")
            return redirect("/login")