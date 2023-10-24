from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import requests
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_session import Session


app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# DB connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# list of currencies available
UNSORTED_CURRENCIES = [
            {"iso":"EUR","name": "Euro"},
            {"iso":"BRL","name": "Brazilian Real"},
            {"iso":"JPY","name": "Japanese yen"},
            {"iso":"GBP","name": "Pound sterling"}, 
            {"iso":"AUD","name": "Australian dollar"}, 
            {"iso":"CAD","name": "Canadian dollar"}, 
            {"iso":"CHF","name": "Swiss franc"}, 
            {"iso":"CNH","name": "Chinese renminbi"}, 
            {"iso":"HKD","name": "Hong Kong dollar"}, 
            {"iso":"NZD","name": "New Zealand dollar"}, 
            {"iso":"MXN","name": "Mexixan peso"}
            ]   

# currencies sorted alphabetically be name value
CURRENCIES = sorted(UNSORTED_CURRENCIES, key=lambda x: x['name'])

# list of currencies iso codes 
CURRENCIES_ISO = [currency['iso'] for currency in CURRENCIES]

def money_format(value):
    return f"${value:,.2f}"

def currency_format(value):
    return f"{value:,.4f}"

app.jinja_env.filters["money_format"] = money_format
app.jinja_env.filters["currency_format"] = currency_format


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
            return redirect("/read")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
    conn.close()

    return render_template("index.html", user=user)
 

@app.route("/register", methods = ["POST", "GET"])
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
        city = request.form.get("city").title().strip()
        state = request.form.get("state").title().strip()
        country = request.form.get("country").title().strip()
        currency = request.form.get("currency").strip()

        # search DB for user_name provided
        conn = get_db_connection()
        db_users = conn.execute("SELECT * FROM users WHERE user_name = ? ", (user_name,)).fetchall()
        
        # check if fields were filled
        if not name or not last_name or not user_name or not password or not confirmation or not city or not state or not country:
            flash("Please fill all fields to register!", "warning")
            return render_template("register.html")
        
        # check if user already exists
        elif len(db_users) != 0:
            flash("User name already exists!", "warning")
            return render_template("register.html")

        # check if passwords match
        elif password != confirmation:
            flash("Passwords do not match, please try again!", "warning")
            return render_template("register.html")

        # validate if currency exists
        elif currency not in CURRENCIES_ISO:
            flash("Currency not valid, please choose one in the select field!", "warning")
            return render_template("register.html")
        
        # if everything is fine
        else:

            hash = generate_password_hash(password)
            # insert new user to db
            conn.execute("INSERT INTO users (name, last_name, user_name, hash, city, state, country, currency, github_username) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, last_name, user_name, hash, city, state, country, currency, github))
            
            conn.commit()

            rows = conn.execute("SELECT * FROM users WHERE user_name = ?", (user_name,)).fetchall()
            conn.close()



            session["user_id"] = rows[0]["id"]
            session["name"] = rows[0]["name"]
            session["currency"] = rows[0]["currency"]

            for currency in CURRENCIES:
                if currency["iso"] == rows[0]["currency"]:
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
        rows = conn.execute("SELECT * FROM users WHERE user_name = ?", (user_name,)).fetchall()
        conn.close()

        if len(rows) != 1:
            flash("User do not exist, please register!", "warning")
            return render_template("register.html")
        
        # check if password saved in DB is equal to password provided
        elif not check_password_hash(rows[0]["hash"], password):
            flash("Incorrect password!", "danger")
            return redirect("/login")


        else:

            session["user_id"] = rows[0]["id"]
            session["name"] = rows[0]["name"]
            session["currency"] = rows[0]["currency"]

            for currency in CURRENCIES:
                if currency["iso"] == rows[0]["currency"]:
                    currency_name = currency["name"]
                    
            session["currency_name"] = currency_name

            # flash(f"{user_name} login", "success")
            return redirect("/")
           

    else: # GET
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

        item_brand = request.form.get("brand").title().strip()
        item_name = request.form.get("name").title().strip()
        item_price = request.form.get("price")
        item_infos = request.form.get("item_infos").capitalize().strip()
        item_link = request.form.get("item_link").strip()
        quantity = request.form.get("quantity").strip()

        user_id = session["user_id"]


        if not item_brand or not item_name or not item_price:
            flash("Please fill all fileds with *", "warning")
            return redirect("/add")
        
        elif not item_price.isdigit() or float(item_price) <= 0:
            flash("Price must be a real positive number", "warning")
            return redirect("/add")
        
        elif not quantity.isdigit() or int(quantity) <= 0:
            flash("Quantity must be a integer positive number", "warning")
            return redirect("/add")

        else:
            conn = get_db_connection()
            conn.execute("INSERT INTO products(name, brand, informations, link, price, user_id, quantity) VALUES (?, ?, ?, ?, ?, ?, ?)", (item_name, item_brand, item_infos, item_link, item_price, user_id, quantity))
            
            conn.commit()
            conn.close()

        flash(f"{item_name} added to your list", "success")
        return redirect("/list")
    
    
    else: # GET
        return render_template("add.html")


@app.route("/list")
@login_required
def list():

    user_id = session["user_id"]
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
    user_products = conn.execute("SELECT * FROM products WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()

    # get user image from github account, if does not have avatar image, so i will render a basic one
    github_username = user[0]["github_username"]
    avatar_url = ""

    if not github_username:
        avatar_url = "/static/avatar.png"
    else:
        github_response = (requests.get(f"https://api.github.com/users/{github_username}")).json()
        avatar_url = github_response['avatar_url']


    # total price of all user's products
    total_price = 0
    total_favorites_price = 0
    product_tax = 1.08

    for product in user_products:
        
        # sum total price of all favorite products
        if product["is_favorite"] == 1:
            product_price = product["price"] * product["quantity"] * product_tax
            total_favorites_price += product_price
    
        # sum all products
        
        product_price = product["price"] * product["quantity"] * product_tax
        total_price += product_price

    # get currency conversion from api
    currency_iso = session["currency"]
    response = requests.get(f"http://economia.awesomeapi.com.br/json/last/USD-{currency_iso}").json()
    conversion = response[f'USD{currency_iso}']['high']

    plus_safety_margin = 1.029 # safety margin in conversion because of the variability
    total_converted = float(total_price) * float(conversion) * plus_safety_margin
    total_favorites_converted = float(total_favorites_price) * float(conversion) * plus_safety_margin

    

    return render_template("list.html", session=session, 
                           conversion=float(conversion),
                           avatar_url=avatar_url, 
                           user_products=user_products, 
                           total_price= total_price, 
                           total_converted=total_converted, 
                           total_favorites_price=total_favorites_price,
                           total_favorites_converted=total_favorites_converted,
                           plus_safety_margin=plus_safety_margin,
                           product_tax=product_tax
                           )
 

@app.route("/favorite", methods=["POST"])
@login_required
def favorite():

    item_id = int(request.form.get("item_id"))

    if not item_id:
        flash("Product could not be found, try another one!", "danger")
        return redirect("/list")
    
    conn = get_db_connection()
    product_infos = conn.execute("SELECT * FROM products WHERE id = ?", (item_id,)).fetchall()
    is_favorite = product_infos[0]['is_favorite']
    product_name = product_infos[0]['name']
    product_brand = product_infos[0]['brand']

    # 0 means that the product is not favorite, so change to favorite by updating is_favorite in DB to 1
    if is_favorite == 0:
        conn.execute("UPDATE products SET is_favorite = 1 WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        flash(f"{product_brand} - {product_name} added to favorites!", "success")
        return redirect("/list")
    
    # 1 means the product is favorite, so remove from favorites by updating is_favorite in DB to 0
    elif is_favorite == 1:
        conn.execute("UPDATE products SET is_favorite = 0 WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        flash(f"{product_brand} - {product_name} removed from favorites!", "success")
        return redirect("/list")
        
    else:
        flash("Internal error! Please try again.", "danger")
        return redirect("/list")
  
# TODO A POPUP TO CONFIRM DELETE PRODUCT ACTION
@app.route("/delete", methods=["POST"])
@login_required
def delete():

    item_id = request.form.get("item_id")
    
    if not item_id:
        return render_template("message.html", message="Item couldn't be deleted")
    else:
        # delete form the database the selected item, with the id we got
        pass
        return render_template("message.html", message=f'item deleted: {item_id}')

# TODO
@app.route("/account", methods=["POST", "GET"])
@login_required
def account():

    if request.method == "POST":

        currency = request.form.get("currency")
        
        # validate if currency exists
        if currency not in CURRENCIES_ISO:
            return render_template("message.html", message="Currency not valid, please choose one in the select field!")
        else:
            return render_template("message.html", message="Currency valid!")
        
    else: # GET
        github_response = (requests.get("https://api.github.com/users/felipedh9")).json()
        avatar_url = github_response['avatar_url']
        if not avatar_url:
            avatar_url = '#'

        return render_template("account.html", avatar_url=avatar_url, currencies=CURRENCIES)
    # return redirect("/")


@app.route("/currency", methods = ["POST", "GET"])
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
            conn.execute("UPDATE users SET currency = ? WHERE id = ?", (currency_iso, user_id,))
            conn.commit()
            conn.close()

            for currency in CURRENCIES:
                if currency["iso"] == currency_iso:
                    currency_name = currency["name"]

            session["currency_name"] = currency_name
            session["currency"] = currency_iso

        flash(f"Currency changed to {currency_iso} ({currency_name})", "success")
        return redirect("/list")
    

    else: #GET
        return render_template("currency.html", currencies=CURRENCIES)

# TODO
@app.route("/edit", methods = ["POST", "GET"])
@login_required
def change():

    if request.method == "POST":

        item_id = request.form.get("item_id")

        item_brand = request.form.get("brand").title().strip()
        item_name = request.form.get("name").title().strip()
        item_price = request.form.get("price")  
        item_infos = request.form.get("item_infos").capitalize().strip()
        item_link = request.form.get("item_link").strip()
        item_quantity = request.form.get("quantity").strip()

        conn = get_db_connection()
        product_before = conn.execute("SELECT * FROM products WHERE id = ?", (item_id,)).fetchall()
        changes = 0
    
  
        # if item_price and not item_price.isdigit() or float(item_price) <= 0:
        #     flash("Price must be a real positive number", "warning")
        #     return redirect("/list")
        
        # elif item_quantity and not item_quantity.isdigit() or int(item_quantity) <= 0:
        #     flash("Quantity must be a integer positive number", "warning")
        #     return redirect("/list")
        # 
        # elif not item_price.isdigit() or float(item_price) <= 0:
        

        if item_brand and item_brand != product_before[0]['brand']:
            conn.execute("UPDATE products SET brand = ? WHERE id = ?", (item_brand, item_id,))          
            changes += 1
            

        if item_name and item_name != product_before[0]['name']:
            conn.execute("UPDATE products SET name = ? WHERE id = ?", (item_name, item_id,))
            changes += 1


        # if item_price and item_price != product_before[0]['price']:

        #     if not item_price.isdigit() or float(item_price) <= 0:
        #         flash("Price must be positive float number", "danger")
        #         return redirect("/edit")
        #     else:
        #         conn.execute("UPDATE products SET price = ? WHERE id = ?", (item_price, item_id,))
        #         changes += 1
        if item_price and item_price != product_before[0]['price'] and item_price.isdigit() and float(item_price) > 0:
            conn.execute("UPDATE products SET quantity = ? WHERE id = ?", (item_quantity, item_id,))
            changes += 1


        if item_infos and item_infos != product_before[0]['informations']:
            conn.execute("UPDATE products SET informations = ? WHERE id = ?", (item_infos, item_id,))
            changes += 1          


        if item_link and item_link != product_before[0]['link']:
            conn.execute("UPDATE products SET link = ? WHERE id = ?", (item_link, item_id,))
            changes += 1

        if item_quantity and item_quantity != product_before[0]['quantity'] and item_quantity.isdigit() and int(item_quantity) > 0:
            conn.execute("UPDATE products SET quantity = ? WHERE id = ?", (item_quantity, item_id,))
            changes += 1
                    


        if changes > 0:
            flash(f"{product_before[0]['brand']} - {product_before[0]['name']} edited!", "success")
            
        else:
            flash(f"No changes in {product_before[0]['brand']} - {product_before[0]['name']}", "warning")

        conn.commit()
        conn.close()
        return redirect("/list")

    else: #GET

        item_id = request.args.get("item_id")
        conn = get_db_connection()
        product = conn.execute("SELECT * FROM products WHERE id = ?", (item_id,)).fetchall()
        conn.close()

        return render_template("edit.html", product=product)    

@app.route("/read")
def read():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()