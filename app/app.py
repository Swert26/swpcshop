from flask import Flask, redirect, render_template, url_for, flash, request, session, jsonify, abort
from dotenv import load_dotenv
load_dotenv()
import os
import sqlite3
from datetime import timedelta
from werkzeug.security import check_password_hash, generate_password_hash
import random
#print(os.system("dir"))
from core.database import Database, products
import secrets

app = Flask(__name__)
app.secret_key = os.getenv("secret")
app.permanent_session_lifetime = timedelta(days=7)

db = Database()

@app.route("/")
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
            flash("Такой пользователь уже есть")
            return redirect("/register")
        
        if not has_errors:
            db.create_new_user(name, password)
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
            flash("Неверные данные")
            return redirect("/login")
        
        if not has_errors:
            user = db.select_user(name)
            if not check_password_hash(user[2], password):
                flash("Неверный пароль")
                return redirect("/login")
            
            session.permanent = True
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["cart"] = []
            token = db.token_gen()
            db.set_token(token, session["name"])
            return redirect("/profile")
        
    return render_template("login.html")

@app.route("/profile")
def profile():
    if not "user_id" in session:
        return redirect("/login")
    
    user_data_dict = db.get_profile(session)
    if user_data_dict["role"] == "admin":
        is_admin = True
    else:
        is_admin = False
    return render_template("profile.html", user_data=user_data_dict, is_admin=is_admin)

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

@app.route("/buy_all")
def buy_all():
    if not "user_id" in session:
        return redirect("/login")
    price = 0

    cart = session.get("cart", [])
    for id in cart:
        if id in products:
            price += products.get(id).get("price")

    return render_template("buy_all.html", products=products, cart=session["cart"], price=price)

@app.route("/buy/submit")
def buy_submit():
    if not "user_id" in session:
        return redirect("/login")
    return render_template("submit.html")

@app.get("/admin_panel")
def admin():
    user_data_dict = db.get_profile(session)
    if user_data_dict["role"] == "admin":
        users = db.get_all_users()
        return render_template("admin.html", users=users)
    else:
        return abort(403)

@app.route("/change/<user_id>", methods=["GET", "POST"])
def change_user(user_id):
    user_data_dict = db.get_profile(session)
    if user_data_dict["role"] == "admin":
        users = db.get_all_users()
        print(users)
        user = users[int(user_id)-1]
        return render_template("change_user_admin.html", user=user)
    else:
        user_data_dict = db.get_profile(session)
        return render_template("change_user.html", user_data=user_data_dict)

@app.post("/change_name/<user_id>")
def change_name(user_id):
    if db.get_profile(session)["role"] == "admin":
        new_name = request.form.get("name")
        db.change_name(user_id, new_name=new_name)
        users = db.get_all_users()
        user = users[int(user_id)-1]
        flash(f"Имя пользователя {user[1]} сменено на: {new_name}", "success")
        return redirect(url_for("admin"))
    else:
        new_name = request.form.get("name")
        db.change_name(session["user_id"], new_name=new_name)
        flash(f"Имя сменено на: {new_name}", "success")
        return redirect(url_for("profile"))

@app.post("/change_password/<user_id>")
def change_password(user_id):
    if db.get_profile(session)["role"] == "admin":
        new_password = request.form.get("password")
        db.change_password(user_id, new_password=new_password)
        users = db.get_all_users()
        user = users[int(user_id)-1]
        flash(f"Пароль пользователя {user[1]} изменён", "success")
        return redirect(url_for("admin"))
    else:
        new_password = request.form.get("password")
        db.change_password(user_id, new_password=new_password)
        flash(f"Пароль изменён", "success")
        return redirect(url_for("profile"))
    
@app.post("/change_role/<user_id>")
def change_role(user_id):
    if db.get_profile(session)["role"] == "admin":
        new_role = request.form.get("role")
        db.change_role(user_id, new_role=new_role)
        users = db.get_all_users()
        user = users[int(user_id)-1]
        flash(f"Роль пользователя {user[1]} сменена на: {new_role}", "success")
        return redirect(url_for("admin"))
    else:
        return abort(403)
    
@app.route("/test_error/<code>")
def test_error(code):
    return abort(int(code))

@app.errorhandler(500)
@app.errorhandler(405)
@app.errorhandler(404)
@app.errorhandler(403)
def error(code):
    return render_template("error.html", error=code)

db.get_db()
db.create_db()
app.run(port=145, debug=True)