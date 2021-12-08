import os
import requests
import json

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions
from decimal import Decimal




app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
data =[]
@app.route('/')
def index():
    if 'username' in session:       
        username = session["username"]
        id_user = db.execute("SELECT id_user FROM users WHERE username = :username",
                          {"username": username}).fetchone()[0]

        items = db.execute("SELECT * FROM todo WHERE user_id=:user_id and complete=false", {"user_id":id_user}).fetchall()
        print(session["user_id"])
        return render_template("index.html",username = session["username"], items=items)
    else:
        
        return render_template("index.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        confirmation = request.form.get("confirmation")
        respuesta = db.execute("SELECT id_user FROM users WHERE username = :username ", {
                               "username": username}).fetchall()
        if len(respuesta) != 0:
            return render_template("register.html", message="username taken")
        if request.form.get("password") != confirmation:
            return render_template("register.html", message="passwords doesn't match")
        password = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users(username, password) VALUES(:username, :password)",
                   {"username": username, "password": password})
        db.commit()
        session["user_id"] = respuesta
        
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        print(username)
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchall()
        print(rows)

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("login.html", message="invalid username and/or password")
        session["user_id"] = rows[0]["id_user"]
        session["username"] = username
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        username = session["username"]
        id_user = db.execute("SELECT id_user FROM users WHERE username = :username",
                          {"username": username}).fetchone()[0]
        text = request.form.get("todoitem")
        print(id_user)
        print(text)
        db.execute("INSERT INTO todo(user_id,text,complete) VALUES(:id_user, :text,false)",
                   {"id_user": id_user, "text": text})
        db.commit()
        flash("saved!")
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    
@app.route("/complete/<id_todo>", methods=["GET", "POST"])
def complete(id_todo):
    
    db.execute("UPDATE todo set complete=true where id_todo=:todo",  {"todo":id_todo})
    db.commit()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(port=3300,debug=True)