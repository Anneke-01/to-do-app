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

@app.route('/')
def index():
    if 'username' in session:
        username = session["username"]
        id_user = db.execute("SELECT id_user FROM users WHERE username=:username",{"username":username}).fetchone()[0]
        items = db.execute("SELECT * FROM todo WHERE user_id=:user_id and complete=false",{"user_id":id_user}).fetchall()
        return render_template("index.html", username=session["username"], items=items)
    else:     
        return redirect(url_for("register"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("register.html", message="Debes proporcionar un nombre de usuario.")
        if not request.form.get("password"):
            return render_template("register.html", message="Debes proporcionar una contraseña")
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", message="Las contraseñas no coinciden")
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        respuesta = db.execute("SELECT id_user FROM users WHERE username = :username ", {
                                "username": username}).fetchall()
        if len(respuesta) != 0:
            return render_template("register.html", message="Usuario ya registrado")
        db.execute("INSERT INTO users(username, password) VALUES(:username, :password)",
                    {"username": username, "password": password})
        db.commit()
        session["user_id"] = respuesta
    
        return redirect(url_for("index"), message="Registrado!")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("register.html", message="Debes proporcionar un nombre de usuario.")
        if not request.form.get("password"):
            return render_template("register.html", message="Debes proporcionar una contraseña")
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        respuesta = db.execute("SELECT * FROM users WHERE username = :username ", {
                                "username": username}).fetchall()
        if len(respuesta) != 1 or not check_password_hash(respuesta[0]["password"], request.form.get("password")):
            return render_template("login.html", message="Nombre de usuario o contraseña incorrectos")
        session["user_id"] = respuesta[0]["id_user"]
        session["username"] = username
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        username = session["username"]
        id_user = db.execute("SELECT id_user FROM users WHERE username=:username",{"username":username}).fetchone()[0]
        text = request.form.get("todoitem")
        db.execute("INSERT INTO todo(user_id, text, complete) VALUES(:id_user,:text,false)",{"id_user":id_user,"text":text})
        db.commit()
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    
@app.route("/completado/<id_todo>", methods=["GET", "POST"])
def completado(id_todo):
    if 'username' in session:
        username = session["username"]
        id_user = db.execute("SELECT id_user FROM users WHERE username=:username",{"username":username}).fetchone()[0]
        db.execute("UPDATE todo SET complete=true WHERE id_todo=:todo and user_id=:id_user", {"todo":id_todo,"id_user":id_user})
        db.commit()
        return redirect(url_for("index"))
   
   
@app.route("/historial", methods=["GET","POST"])
def historial():
    if 'username' in session:
        username = session["username"]
        id_user = db.execute("SELECT id_user FROM users WHERE username=:username",{"username":username}).fetchone()[0]
        items = db.execute("SELECT * FROM todo WHERE user_id=:user_id and complete=true",{"user_id":id_user}).fetchall()
        return render_template("historial.html", items=items)
    else:
        return render_template("historial.html")
@app.route("/eliminarHistorial",methods=["GET","POST"])
def eliminarHistorial():
    print("EEE")
    username = session["username"]
    id_user = db.execute("SELECT id_user FROM users WHERE username=:username",{"username":username}).fetchone()[0]
    items = db.execute("SELECT * FROM todo WHERE user_id=:user_id and complete=true",{"user_id":id_user}).fetchall()
    if len(items) != 1:
        return render_template("historial.html",items=items)
    else:
        items = db.execute("DELETE FROM todo WHERE user_id=:user_id and complete=true",{"user_id":id_user})
        return render_template("historial.html" )
    
    
    
 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
if __name__ == '__main__':
    app.run(port=3300,debug=True)