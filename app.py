from flask import Flask, redirect, render_template, url_for, flash, request, session, jsonify
from dotenv import load_dotenv
load_dotenv()
import os
import sqlite3
from datetime import timedelta
from werkzeug.security import check_password_hash, generate_password_hash
import random
from database import Database, products

app = Flask(__name__)
app.secret_key = os.getenv("secret")
app.permanent_session_lifetime = timedelta(days=7)

db = Database()

@app.route("/")
def index():
    return redirect("/home")

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        has_errors = False

        if db.check_user(name):
            has_errors = True
            return redirect("/register")
        
        if not has_errors:
            password_hash = generate_password_hash(password)

            con = db.get_db()
            con.execute("""INSERT INTO users (name, password_hash) VALUES (?, ?)""", (name, password_hash))
            con.commit()
            con.close()
            
            return redirect("/login")
        
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        has_errors = False

        if not db.check_user(name):
            has_errors = True
            return redirect("/register")
        
        if not has_errors:
            con = db.get_db()
            user = con.execute("""SELECT * FROM USERS WHERE name = ?""", (name, )).fetchone()
            con.close()
            if not check_password_hash(user[2], password):
                return redirect("/register")
            
            session.permanent = True
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["cart"] = []
            return redirect("/profile")
        
    return render_template("login.html")

@app.route("/profile")
def profile():
    if not "user_id" in session:
        return redirect("/login")
    
    con = db.get_db()
    user_data = con.execute("""SELECT * FROM users WHERE name = ?""", (session["name"], )).fetchone()
    user_data_dict = {
        "name": user_data[1],
        "id": user_data[0]
    }
    return render_template("profile.html", user_data=user_data_dict)

@app.route("/catalog")
def catalog():
    return render_template("catalog.html", products=products)

@app.route("/cart")
def cart():
    if not "user_id" in session:
        return redirect("/login")
    print(session["cart"])
    cart = session.get("cart", [])
    return render_template("cart.html", cart=cart, products=products)

@app.route("/cart/add/<item>")
def cart_add(item):
    if not "user_id" in session:
        return redirect("/login")
    try:
        item_id = int(item)
    except:
        return "Incorrect id"
    
    currect_cart = session.get("cart", [])
    currect_cart.append(item_id)
    session["cart"] = currect_cart
    print(currect_cart)
    return redirect("/cart")

@app.route("/cart/delete/<item>")
def cart_delete(item):
    if not "user_id" in session:
        return redirect("/login")
    try:
        item_id = int(item)
    except:
        return "Incorrect id"
    
    currect_cart = session.get("cart", [])
    try:
        currect_cart.remove(item_id)
        session["cart"] = currect_cart
        print(currect_cart)
        return redirect("/cart")
    except:
        return "Incorrect id"

@app.route("/buy/<id>")
def buy(id):
    if not "user_id" in session:
        return redirect("/login")
    try:
        item_id = int(id)
    except IndexError or TypeError:
        return "Incorrect id"
    return render_template("buy.html", products=products, id=item_id)

@app.route("/buy/submit")
def buy_submit():
    if not "user_id" in session:
        return redirect("/login")
    return render_template("submit.html")

@app.errorhandler(404)
def error404(code):
    return f"YOU FORGOT A HEAD? {404}"

db.get_db()
db.create_db()
app.run(port=145, debug=True)