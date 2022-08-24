
from crypt import methods
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect


app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get["name"]
        print(name)
        return redirect("index.html")
    else:
        return render_template("register.html")


@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/bla", methods = ["POST"])
def bla():
    name = request.form.get("name")
    return render_template("bla.html",name=name)
    