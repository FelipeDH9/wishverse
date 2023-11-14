from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import requests
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_session import Session
from decimal import Decimal, InvalidOperation
# from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SECRET_KEY'] = 'C098WNFD021LPA834asdcxzsadrwe32342'
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# db = SQLAlchemy(app)

# class 


# DB connection
def get_db_connection():
    conn = sqlite3.connect("postgres://kolposefgivsfg:f55297fb1552520b77a14e2919c93e6430762fedb89aa78499140933412274d6@ec2-18-213-255-35.compute-1.amazonaws.com:5432/da2v8nmgjslig3")
    conn.row_factory = sqlite3.Row
    return conn


# list of currencies available
UNSORTED_CURRENCIES = [
    {"iso": "EUR", "name": "Euro"},
    {"iso": "BRL", "name": "Brazilian Real"},
    {"iso": "JPY", "name": "Japanese yen"},
    {"iso": "GBP", "name": "Pound sterling"},
    {"iso": "AUD", "name": "Australian dollar"},
    {"iso": "CAD", "name": "Canadian dollar"},
    {"iso": "CHF", "name": "Swiss franc"},
    {"iso": "CNH", "name": "Chinese renminbi"},
    {"iso": "HKD", "name": "Hong Kong dollar"},
    {"iso": "NZD", "name": "New Zealand dollar"},
    {"iso": "MXN", "name": "Mexixan peso"},
]

# currencies sorted alphabetically be name value
CURRENCIES = sorted(UNSORTED_CURRENCIES, key=lambda x: x["name"])

# list of currencies iso codes
CURRENCIES_ISO = [currency["iso"] for currency in CURRENCIES]


def money_format(value):
    return f"${value:,.2f}"


def currency_format(value):
    return f"{value:,.4f}"


def get_github(github):
    github_response = (requests.get(f"https://api.github.com/users/{github}"))            

    if github_response.status_code == 200:
        response = github_response.json()
        session['avatar_url'] = response["avatar_url"]
    else:
        session['avatar_url'] = "/static/avatar.png"
    
    return session['avatar_url']


def is_decimal(n):
    try:
        Decimal(n)
        return True
    except InvalidOperation:
        return False

app.jinja_env.filters["money_format"] = money_format
app.jinja_env.filters["currency_format"] = currency_format

# tax over products
PRODUCT_TAX = 1.08


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/about")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    # clear session
    session.clear()

    if request.method == "POST":
        name = request.form.get("name").title().strip()
        last_name = request.form.get("last_name").title().strip()
        user_name = request.form.get("user_name").strip()
        github = request.form.get("github").strip()
        password = request.form.get("password").strip()
        confirmation = request.form.get("confirmation").strip()
        country = request.form.get("country").title().strip()
        currency = request.form.get("currency")
        linkedin = request.form.get("linkedin").strip()

        # search DB for user_name provided
        conn = get_db_connection()
        db_users = conn.execute(
            "SELECT * FROM users WHERE user_name = ? ", (user_name,)
        ).fetchall()

        # check if fields were filled
        if (
            not name
            or not last_name
            or not user_name
            or not password
            or not confirmation
            or not country
        ):
            flash("Please fill all fields to register!", "warning")
            return render_template("register.html", currencies=CURRENCIES)

        # check if user already exists
        elif len(db_users) != 0:
            flash("User name already exists!", "warning")
            return render_template("register.html", currencies=CURRENCIES)

        # check if passwords match
        elif password != confirmation:
            flash("Passwords do not match, please try again!", "warning")
            return render_template("register.html", currencies=CURRENCIES)

        # validate if currency exists
        elif currency not in CURRENCIES_ISO:
            flash(
                "Currency not valid, please choose one in the select field!", "warning"
            )
            return render_template("register.html", currencies=CURRENCIES)
        
            
            
        # if everything is fine
        else:
            hash = generate_password_hash(password)
            # insert new user to db
            conn.execute(
                "INSERT INTO users (name, last_name, user_name, hash, country, currency, github, linkedin) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    name,
                    last_name,
                    user_name,
                    hash,
                    country,
                    currency,
                    github,
                    linkedin,
                ),
            )

            conn.commit()

            user = conn.execute(
                "SELECT * FROM users WHERE user_name = ?", (user_name,)
            ).fetchall()
            conn.close()

            session["user_id"] = user[0]["id"]
            session["name"] = user[0]["name"]
            session["last_name"] = user[0]["last_name"]
            session["user_name"] = user[0]["user_name"]
            session["country"] = user[0]["country"]
            session["currency"] = user[0]["currency"]
            session["linkedin"] = user[0]["linkedin"]

                   
            
            get_github(github)
           

            for currency in CURRENCIES:
                if currency["iso"] == user[0]["currency"]:
                    currency_name = currency["name"]

            session["currency_name"] = currency_name

            flash(f"New user ({user_name}) registred", "success")
            return redirect("/")

    # GET
    else:
        return render_template("register.html", currencies=CURRENCIES)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        user_name = request.form.get("user_name").strip()
        password = request.form.get("password").strip()

        # Ensure username was submitted
        if not user_name:
            flash("Username must be provided!", "warning")
            return redirect("/login")

        # Ensure password was submitted
        elif not password:
            flash("Password must be provided!", "warning")
            return redirect("/login")

        # Query database for username
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE user_name = ?", (user_name,)
        ).fetchall()
        conn.close()

        if len(user) != 1:
            flash("User do not exist, please register!", "warning")
            return render_template("register.html", currencies=CURRENCIES)

        # check if password saved in DB is equal to password provided
        elif not check_password_hash(user[0]["hash"], password):
            flash("Incorrect password!", "danger")
            return redirect("/login")

        else:
            github = user[0]["github"]
            get_github(github)
            

            session["user_id"] = user[0]["id"]
            session["name"] = user[0]["name"]
            session["last_name"] = user[0]["last_name"]
            session["user_name"] = user[0]["user_name"]
            session["country"] = user[0]["country"]
            session["github"] = user[0]["github"]
            session["currency"] = user[0]["currency"]


            for currency in CURRENCIES:
                if currency["iso"] == user[0]["currency"]:
                    currency_name = currency["name"]

            session["currency_name"] = currency_name

            return redirect("/list")

    else:  # GET
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logout", "danger")
    return redirect("/")


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    if request.method == "POST":
        product_brand = request.form.get("brand").title().strip()
        product_name = request.form.get("name").title().strip()
        product_price = request.form.get("price")
        product_infos = request.form.get("infos").capitalize().strip()
        product_link = request.form.get("link").strip()
        product_quantity = request.form.get("quantity").strip()

        user_id = session["user_id"]

        if not product_brand or not product_name or not product_price:
            flash("Please fill all fileds with *", "warning")
            return redirect("/add")

        # elif not product_price.isdigit() or float(product_price) <= 0:
        #     flash("Price must be a real positive number", "warning")
        #     return redirect("/add")
        
        elif not is_decimal(product_price) or float(product_price) <= 0:
            flash("Price must be a real positive number", "warning")
            return redirect("/add")


        elif not product_quantity.isdigit() or int(product_quantity) <= 0:
            flash("Quantity must be a integer positive number", "warning")
            return redirect("/add")

        else:
            product_price = float(product_price)
            product_quantity = int(product_quantity)

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO products(name, brand, informations, link, price, user_id, quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    product_name,
                    product_brand,
                    product_infos,
                    product_link,
                    product_price,
                    user_id,
                    product_quantity,
                ),
            )

            conn.commit()
            conn.close()

        flash(f"{product_name} added to your list", "success")
        return redirect("/list")

    else:  # GET
        return render_template("add.html")


@app.route("/list")
@login_required
def list():
    user_id = session["user_id"]

    conn = get_db_connection()
    user_products = conn.execute(
        "SELECT * FROM products WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()

    # total price of all user's products
    total_price = 0
    total_favorites_price = 0
    

    for product in user_products:
        # sum total price of all favorite products
        if product["is_favorite"] == 1:
            product_price = float(product["price"]) * float(product["quantity"]) * PRODUCT_TAX
            total_favorites_price += product_price

        # sum all products

        product_price = product["price"] * product["quantity"] * PRODUCT_TAX
        total_price += product_price

    # get currency conversion from api
    currency_iso = session["currency"]
    response = requests.get(
        f"http://economia.awesomeapi.com.br/json/last/USD-{currency_iso}"
    ).json()
    conversion = response[f"USD{currency_iso}"]["high"]

    plus_safety_margin = 1.029  # safety margin in conversion because of the variability
    total_converted = float(total_price) * float(conversion) * plus_safety_margin
    total_favorites_converted = (
        float(total_favorites_price) * float(conversion) * plus_safety_margin
    )

    return render_template(
        "list.html",
        session=session,
        conversion=float(conversion),
        user_products=user_products,
        total_price=total_price,
        total_converted=total_converted,
        total_favorites_price=total_favorites_price,
        total_favorites_converted=total_favorites_converted,
        plus_safety_margin=plus_safety_margin,
        product_tax=PRODUCT_TAX,
    )


@app.route("/favorite", methods=["POST"])
@login_required
def favorite():
    product_id = request.form.get("product_id")

    if not product_id or not product_id.isdigit() or int(product_id) <= 0:
        flash(f"Product {product_id} could not be found , try another one!", "danger")
        return redirect("/list")

    conn = get_db_connection()

    # GET ALL USER PRODUCTS ID'S
    id_counter = conn.execute("SELECT id FROM products WHERE user_id = ?", (session["user_id"],)).fetchall()
    id_list = []
    for id in id_counter:
        id_list.append(id['id'])

    
    if int(product_id) not in id_list:
        flash(f"Product {product_id} could not be found {id_list}, try another one!", "danger")
        return redirect("/list")
    
    else:
        conn = get_db_connection()
        product_infos = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchall()
        is_favorite = product_infos[0]["is_favorite"]
        product_name = product_infos[0]["name"]
        product_brand = product_infos[0]["brand"]

        # 0 means that the product is not favorite, so change to favorite by updating is_favorite in DB to 1
        if is_favorite == 0:
            conn.execute("UPDATE products SET is_favorite = 1 WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            flash(f"{product_brand} - {product_name} added to favorites!", "success")
            return redirect("/list")

        # 1 means the product is favorite, so remove from favorites by updating is_favorite in DB to 0
        elif is_favorite == 1:
            conn.execute("UPDATE products SET is_favorite = 0 WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            flash(f"{product_brand} - {product_name} removed from favorites!", "success")
            return redirect("/list")

        else:
            flash("Internal error! Please try again.", "danger")
            return redirect("/list")


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    product_id = request.form.get("product_id")

    if not product_id or not product_id.isdigit() or int(product_id) <= 0:
        flash(f"Product {product_id} could not be found , try another one!", "danger")
        return redirect("/list")

    conn = get_db_connection()

    # GET ALL USER PRODUCTS ID'S
    id_counter = conn.execute("SELECT id FROM products WHERE user_id = ?", (session["user_id"],)).fetchall()
    id_list = []
    for id in id_counter:
        id_list.append(id['id'])

    
    if int(product_id) not in id_list:
        flash(f"Product {product_id} could not be found {id_list}, try another one!", "danger")
        conn.close()
        return redirect("/list")
    
    else:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        flash("Product deleted", "warning")
        return redirect('/list')  


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_name = request.form.get("name").strip().title()
        new_last_name = request.form.get("last_name").strip().title()
        new_password = request.form.get("password").strip()
        new_confirmation = request.form.get("confirmation").strip()
        new_country = request.form.get("country").strip().title()
        new_github = request.form.get("github").strip()
        new_linkedin = request.form.get("linkedin")

        if not user_id or not user_id.isdigit() or int(user_id) <= 0:
            flash(f"User {user_id} do not exist, try another one!", "danger")
            return redirect("/list")
        
        # check if requested id is equal to id saved in session  
        elif int(session["user_id"]) != int(user_id):
            flash(f"User {user_id} session: {session['user_id']} could not be found , try another one!", "danger")
            return redirect("/list")
        
        # if user_id is correct
        else:
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
            changes = 0


            # check name
            if new_name and new_name != user[0]["name"]:
                conn.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id,))
                changes += 1
                session["name"] = new_name
            

            # check last name  
            if new_last_name and new_last_name != user[0]["last_name"]:
                conn.execute("UPDATE users SET last_name = ? WHERE id = ?", (new_last_name, user_id,))
                changes += 1
                session["last_name"] = new_last_name

                           
            # check country 
            if new_country and new_country != user[0]["country"]:
                conn.execute("UPDATE users SET country = ? WHERE id = ?", (new_country, user_id,))
                changes += 1
                session["country"] = new_country
                

            # check github
            if new_github and new_github != user[0]["github"]:
                conn.execute("UPDATE users SET github = ? WHERE id = ?", (new_github, user_id,))
                get_github(new_github)
                session["github"] = new_github
                changes += 1
            
            # check password 
            if new_password and new_confirmation and new_password == new_confirmation:
                hash = generate_password_hash(new_password)
                conn.execute("UPDATE users SET hash = ? WHERE id = ?", (hash, user_id,))
                changes += 1
            
            # check linkedin
            if new_linkedin and new_linkedin != user[0]["linkedin"]:
                conn.execute("UPDATE users SET linkedin = ? WHERE id = ?", (new_linkedin.strip(), user_id,))
                changes += 1
                session["linkedin"] = new_linkedin

            
            if changes > 0:
                flash(f"User {session['user_name']} edited!","success",)

            else:
                flash(f"No changes in user {session['user_name']}","warning",)


            conn.commit()
            conn.close()
            return redirect("/list")


    else:  # GET
        user_id = request.args.get("user_id")

        # check if the requested id exist, is a positive integer
        if not user_id or not user_id.isdigit() or int(user_id) <= 0:
            flash(f"User {user_id} could not be found , try another one!", "danger")
            return redirect("/list")
        
        # check if requested id is equal to id saved in session  
        elif int(session["user_id"]) != int(user_id):
            flash(f"User {user_id} could not be found , try another one!", "danger")
            return redirect("/list")
        
        # all fine
        else:
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
            conn.close()

            return render_template("account.html", currencies=CURRENCIES, user=user)


@app.route("/currency", methods=["POST", "GET"])
@login_required
def currency():
    user_id = session["user_id"]

    # change currency in the database
    if request.method == "POST":
        currency_iso = request.form.get("currency")

        if currency_iso not in CURRENCIES_ISO:
            flash("Currency invalid, choose one in the select field!", "danger")
            return redirect("/currency")

        else:
            conn = get_db_connection()
            conn.execute(
                "UPDATE users SET currency = ? WHERE id = ?",
                (
                    currency_iso,
                    user_id,
                ),
            )
            conn.commit()
            conn.close()

            for currency in CURRENCIES:
                if currency["iso"] == currency_iso:
                    currency_name = currency["name"]

            session["currency_name"] = currency_name
            session["currency"] = currency_iso

        flash(f"Currency changed to {currency_iso} ({currency_name})", "success")
        return redirect("/list")

    else:  # GET
        return render_template("currency.html", currencies=CURRENCIES)


@app.route("/edit", methods=["POST", "GET"])
@login_required
def change():
    if request.method == "POST":
        product_id = request.form.get("product_id")

        product_brand = request.form.get("brand").title().strip()
        product_name = request.form.get("name").title().strip()
        product_price = request.form.get("price")
        product_infos = request.form.get("infos").capitalize().strip()
        product_link = request.form.get("link").strip()
        product_quantity = request.form.get("quantity").strip()
        
        
        if not product_id or int(product_id) < 1 or product_id != session["product_id"]:
            flash("Product could not be found, try another one!", "danger")
            return redirect("/list")
        
        
        conn = get_db_connection()
        product_before = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchall()
        changes = 0

        if product_brand and product_brand != product_before[0]["brand"]:
            conn.execute(
                "UPDATE products SET brand = ? WHERE id = ?",
                (
                    product_brand,
                    product_id,
                ),
            )
            changes += 1

        if product_name and product_name != product_before[0]["name"]:
            conn.execute(
                "UPDATE products SET name = ? WHERE id = ?",
                (
                    product_name,
                    product_id,
                ),
            )
            changes += 1


        if product_infos and product_infos != product_before[0]["informations"]:
            conn.execute(
                "UPDATE products SET informations = ? WHERE id = ?",
                (
                    product_infos,
                    product_id,
                ),
            )
            changes += 1

        if product_link and product_link != product_before[0]["link"]:
            conn.execute(
                "UPDATE products SET link = ? WHERE id = ?",
                (
                    product_link,
                    product_id,
                ),
            )
            changes += 1      
        
        if (
            product_price
            and product_price != product_before[0]["price"]
            and is_decimal(product_price)
            and float(product_price) > 0
        ):
            conn.execute(
                "UPDATE products SET price = ? WHERE id = ?",
                (
                    product_price,
                    product_id,
                ),
            )
            changes += 1

        if (
            product_quantity is not None
            and product_quantity != product_before[0]["quantity"]
            and product_quantity.isdigit()
            and int(product_quantity) > 0
        ):
            conn.execute(
                "UPDATE products SET quantity = ? WHERE id = ?",
                (
                    product_quantity,
                    product_id,
                ),
            )
            changes += 1

        if changes > 0:
            flash(
                f"{product_before[0]['brand']} - {product_before[0]['name']} edited!",
                "success",
            )

        else:
            flash(
                f"No changes in {product_before[0]['brand']} - {product_before[0]['name']}",
                "warning",
            )

        conn.commit()
        conn.close()
        return redirect("/list")

    else:  # GET
        product_id = request.args.get("product_id")

        if not product_id or not product_id.isdigit() or int(product_id) <= 0:
            flash(f"Product {product_id} could not be found , try another one!", "danger")
            return redirect("/list")

        conn = get_db_connection()

        # GET ALL USER PRODUCTS ID'S
        id_counter = conn.execute("SELECT id FROM products WHERE user_id = ?", (session["user_id"],)).fetchall()
        id_list = []
        for id in id_counter:
            id_list.append(id['id'])

        
        if int(product_id) not in id_list:
            flash(f"Product {product_id} could not be found {id_list}, try another one!", "danger")
            return redirect("/list")
        
        else:
            product = conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchall()
            conn.close()

            session["product_id"] = product_id
        

        return render_template("edit.html", product=product)


@app.route("/about")
def about():
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('message.html', message="Page not found, 404"), 404


if __name__ == "__main__":
    app.run()
