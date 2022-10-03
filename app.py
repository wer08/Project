from asyncore import read
from time import strftime
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_session import Session
from passlib.hash import sha256_crypt
from datetime import date,datetime
import sqlite3
from flask_mail import Mail,Message
from werkzeug.utils import secure_filename
import stripe
import os

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

#Create Stripe payment 
stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']


app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '1d1815f802c68f'
app.config['MAIL_PASSWORD'] = '13b217b9a01d7d'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

    
@app.route("/", methods=["GET","POST"])
def index():
    flag=True
    if not session:
        flag=False

    choice = request.form.get("choice",False)
    airports_cursor = db.execute("SELECT city,name FROM airport")
    airports = airports_cursor.fetchall()
    today = date.today()
    d = today.strftime("%Y-%m-%d")
    if request.method == "POST":
        departure = request.form.get("departure")
        session["departure"] = departure
        arrival = request.form.get("arrival")
        if departure == arrival:
            flash("You have to choose different airports")
            return redirect("/")
        session["arrival"] = arrival
        date_departure = request.form.get("date-of-departure")
        if not date_departure:
            flash("Enter date of departure")
            return redirect("/")
        date_depart_format = datetime.strptime(date_departure,"%Y-%m-%d")
        date_depart_format = date_depart_format.strftime("%d.%m.%Y")
        adults = int(request.form.get("adults"))
        underage = int(request.form.get("underage"))
        id_departures = db.execute("SELECT id FROM airport WHERE name = ?",(departure,))
        con.commit()
        id_departure = id_departures.fetchone()
        id_arrivals = db.execute("SELECT id FROM airport WHERE name = ?",(arrival,))
        con.commit()
        id_arrival = id_arrivals.fetchone()
        data_tuple = (id_departure[0],id_arrival[0],date_depart_format)
        flights_to_cursor = db.execute("SELECT * FROM flight WHERE departure_id = ? AND arrival_id = ? AND date = ?",data_tuple)
        con.commit()
        flights_to = flights_to_cursor.fetchall()
        if not flights_to:
            flash("There is no flight on that day")
            return redirect("/")
        session["flights"] = flights_to
        if choice == "two":
            date_return = request.form.get("date-of-return")
            date_return_format = datetime.strptime(date_return,"%Y-%m-%d")
            date_return_format = date_return_format.strftime("%d.%m.%Y")
            data_tuple2 = (id_arrival[0],id_departure[0],date_return_format)
            flights_from_cursor = db.execute("SELECT * FROM flight WHERE departure_id = ? AND arrival_id = ? AND date = ?",data_tuple2)
            con.commit()
            flights_from = flights_from_cursor.fetchall()
            if not flights_from:
                flash("There is no return flight on that day")
                return redirect("/")
            flights = {}
            for flight_from in flights_from:
                for flight_to in flights_to:
                    flights[flight_from] = flight_to
                    break
            session["flights"] = flights
            return render_template("index.html",d=d,airports=airports,departure=session["departure"],arrival=session["arrival"],flights=session["flights"],choice=choice,flag=flag,adults=adults,underage=underage)
        else:
            return render_template("index.html",d=d,airports=airports,departure=session["departure"],arrival=session["arrival"],flights=session["flights"],choice=choice,flag=flag,adults=adults,underage=underage)
    else:
        return render_template("index.html",d=d,airports=airports,departure="",arrival="",flights=[],choice=choice,flag=flag,adults=0,underage=0)

@app.route("/buy", methods=["GET","POST"])
def buy():
    if request.method == "GET":
        session["price"]=None
        price = request.args.get("flight_price")
        session["price"] = price
        chosen_to=request.args.get("flight_to")
        chosen_from=request.args.get("flight_from")
        choice=request.args.get("type")
        data_tuple = (chosen_to,)
        data_tuple2 = (chosen_from,)
        flight_to_cursor = db.execute("SELECT * FROM flight WHERE id = ?",data_tuple)
        flight_to = flight_to_cursor.fetchone()
        session["flight_to"] = flight_to
        flight_from_cursor = db.execute("SELECT * FROM flight WHERE id = ?",data_tuple2)
        con.commit()
        flight_from = flight_from_cursor.fetchone()
        session["flight_from"] = flight_from
    if(request.method == "POST"):
        bags = request.form.get("bags")
        bags_price = float(bags) * 10
        session["price"] = float(bags_price) + float(session["price"])
        return render_template("charge.html",key=stripe_keys['publishable_key'],price=session["price"])
    return render_template("buy.html",flight_to=flight_to,flight_from=flight_from,departure=session["departure"],arrival=session["arrival"],choice=choice,price=price)
 

@app.route("/bought")
def bought():
    booked_flights = []
    booked_flights_id_cursor = db.execute("SELECT flight_id FROM booked WHERE user_id=?",(session["id"],)) 
    con.commit()
    booked_flights_id = booked_flights_id_cursor.fetchall()
    for booked_flight_id in booked_flights_id:
        booked_flight_cursor = db.execute("SELECT * FROM flight WHERE id = ?",booked_flight_id)
        con.commit()
        booked_flight = booked_flight_cursor.fetchone()
        departure_cursor = db.execute("SELECT name FROM airport WHERE id = ?",(booked_flight[1],))
        con.commit()
        departure = departure_cursor.fetchone()
        departure = departure[0]
        arrival_cursor = db.execute("SELECT name FROM airport WHERE id = ?",(booked_flight[2],))
        con.commit()
        arrival = arrival_cursor.fetchone()
        arrival = arrival[0]
        date_cursor = db.execute("SELECT date FROM flight WHERE id = ?",booked_flight_id)
        date_of_flight = date_cursor.fetchone()
        date_of_flight = date_of_flight[0]
        flight = (departure,arrival,booked_flight[3],booked_flight[4],booked_flight[5],date_of_flight) 
        booked_flights.append(flight)
        
    return render_template("bought.html",booked_flights=booked_flights)


@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = int(float(session["price"]) * 100)

    customer = stripe.Customer.create(
        email='customer@example.com',
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Price'
    )

    e_mail = db.execute("SELECT email FROM users WHERE username = ?",(session["name"],))
    msg = Message('Ticket purchase confirmation', sender = 'peter@mailtrap.io', recipients = ['paul@mailtrap.io'])
    msg.body = "Ticket bought"
    mail.send(msg)
    flight_to = session["flight_to"]
    flight_from = session["flight_from"]
    if session["flight_to"]:
        db.execute("INSERT INTO booked (user_id,flight_id) VALUES (?,?)",(session["id"],flight_to[0]))
        flash("Ticket succesfully bought")
    if session["flight_from"]:
        db.execute("INSERT INTO booked (user_id,flight_id) VALUES (?,?)",(session["id"],flight_from[0]))
        flash("Ticket succesfully bought")
    return redirect("/bought")

@app.route("/profil",methods=["GET","POST"])
def profil():
    if request.method == "GET":
        users= db.execute("SELECT * FROM users WHERE username = ?",(session["name"],))
        con.commit()
        user = users.fetchone()
        username = user[1]
        name = user[2]
        surname = user[3]
        email = user[4]
        return render_template("profil.html",username=username,name=name,surname=surname,email=email,picture=session["picture"])
    else:
        username = request.form.get("username")
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        users = db.execute("SELECT username, email FROM users WHERE NOT username = ?",(session["name"],))
        con.commit()
        for user in users:
            if user[0] == username or user[1] == email:
                flash('There is user with this username or email')
                return redirect("/profil")
        db.execute("UPDATE users SET username = ? , name = ? , surname = ? , email = ? WHERE username = ?",[username,name,surname,email,session["name"]])
        con.commit()
        flash('You changed personal information')
        session["name"] = username
        return render_template("profil.html",username=username,name=name,surname=surname,email=email)
        


@app.route("/logout")
def logout():
    flash('You are logout')
    session.clear()
    return redirect("/")

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("inputUsername")
        password = request.form.get("inputPassword")
        users = db.execute("SELECT * FROM users")
        con.commit()
        for user in users:
            if username == user[1]:
                passwords = db.execute("SELECT hashed_password FROM users WHERE username = ?",(user[1],))
                con.commit()
                for hash in passwords:
                    if sha256_crypt.verify(password,hash[0]):
                        flash('You were successfully logged in')
                        session["name"] = username
                        session["id"] = user[0]
                        session["picture"] = user[7]
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
        session["picture"] = picture
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
            con.commit()
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