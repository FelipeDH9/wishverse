from flask import Flask, render_template, request, redirect, session
import sqlite3
import requests
from werkzeug.security import check_password_hash, generate_password_hash

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
            {"iso":"MXN","name": "Mexixan peso"},
            {"iso":"ETH","name": "Ethereum"},
            {"iso":"BTC","name": "Bitcoin"},
            {"iso":"XAU","name": "Gold"}
            ]   

# currencies sorted alphabetically be name value
CURRENCIES = sorted(UNSORTED_CURRENCIES, key=lambda x: x['name'])

# list of currencies iso codes 
CURRENCIES_ISO = [currency['iso'] for currency in CURRENCIES]

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():

    # session["user_id"]
    # if not session["user_id"]:

    #     return render_template("index.html")
    
    # else:
    #     user_id = session["user_id"]
    user_id = session["user_id"]

    # if not log in, render the home page which explains what the application is
    # if not session["user_id"]:
    #     return render_template("index.html")
    
    # # if has session, than render the index which shows the users products
    # else:
    #     return render_template("list.html", session=session)

    return render_template("index.html")
    
    # if has session, than render the index which shows the users products
    # else:
    #     return render_template("list.html", session=session)

@app.route("/register", methods = ["POST", "GET"])
def register():

    # clear session
    session.clear()

    if request.method == "POST":

        name = request.form.get("name").title()
        last_name = request.form.get("last_name").title()
        user_name = request.form.get("user_name")
        github = request.form.get("github")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        city = request.form.get("city").title()
        state = request.form.get("state").title()
        country = request.form.get("country").title()
        currency = request.form.get("currency")

        # search DB for user_name provided
        conn = get_db_connection()
        db_users = conn.execute("SELECT * FROM users WHERE user_name = ? ", (user_name,)).fetchall()
        
        # check if fields were filled
        if not name or not last_name or not user_name or not password or not confirmation or not city or not state or not country:
            return render_template("message.html", message="Please fill all fields to register!")
        
        # check if user already exists
        elif len(db_users) != 0:
            return render_template("message.html", message="User name already exists!")

        # check if passwords match
        elif password != confirmation:
            return render_template("message.html", message="Passwords do not match, please try again!")

        # validate if currency exists
        elif currency not in CURRENCIES_ISO:
            return render_template("message.html", message="Currency not valid, please choose one in the select field!")
        
        # if everything is fine
        else:

            hash = generate_password_hash(password)
            # insert new user to db
            conn.execute("INSERT INTO users (name, last_name, user_name, hash, city, state, country, currency, github_username) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, last_name, user_name, hash, city, state, country, currency, github))
            
            conn.commit()

            user_id = conn.execute("SELECT id FROM users WHERE user_name = ?", (user_name,)).fetchall()
            conn.close()

            session["user_id"] = user_id[0]["id"]
            return redirect("/")


    # GET
    else:
        return render_template("register.html", currencies=CURRENCIES)
    

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":

        # Forget any user_id
        session.clear()

        user_name = request.form.get("user_name")
        password = request.form.get("password")

        # Ensure username was submitted
        if not user_name:
            return render_template("message.html", message="Username must be provided!")

        # Ensure password was submitted
        elif not password:
            return render_template("message.html", message="Password must be provided!")
            
        # Query database for username
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM users WHERE user_name = ?", (user_name,)).fetchall()
        conn.close()

        if len(rows) != 1:
            return render_template("message.html", message="User do not exist, please register")
        
        # check if password salved in DB is equal to password provided
        elif not check_password_hash(rows[0]["hash"], password):
            return render_template("message.html", message="Incorrect password")

        else:

            session["user_id"] = rows[0]["id"]

            return redirect("/")
           

    else: # GET
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    # res = requests.get("http://economia.awesomeapi.com.br/json/last/USD-BRL")

    # https://avatars.githubusercontent.com/u/90584577?v=4
    # <Response [200]>


    # res = res.json()
    # {'USDBRL': {'code': 'USD', 'codein': 'BRL', 'name': 'Dólar Americano/Real Brasileiro', 'high': '5.083', 'low': '5.0196', 'varBid': '-0.008', 'pctChange': '-0.16', 'bid': '5.0508', 'ask': '5.0515', 'timestamp': '1697743091', 'create_date': '2023-10-19 16:18:11'}}
    
    
    # res = res['USDBRL']['high']
    # 5.083

    # return render_template("message.html")
    # return redirect("/")

@app.route("/list")
def list():

    session = {}
    session["user_id"] = 1
    session["user_name"] = "FelipeDH"

    github_response = (requests.get("https://api.github.com/users/felipedh9")).json()
    avatar_url = github_response['avatar_url']
    
    if not avatar_url:
        avatar_url = '#'
    if session["user_id"]:
        return render_template("list.html", session=session, avatar_url=avatar_url)
    else:
        return redirect("/")


@app.route("/add", methods=["POST", "GET"])
def add():

    if request.method == "POST":

        item_brand = request.form.get("brand")
        item_name = request.form.get("name")
        item_price = request.form.get("price")
        item_infos = request.form.get("item_infos")
        item_tax = request.form.get("has_tax")
        item_link = request.form.get("item_link")

        if not item_brand or not item_name or not item_price or not item_tax:
            return render_template("message.html", message="Please fill all fileds with *")
        else:
            # add to the database
            pass
        return render_template("message.html", message="Item added")
    else: # GET
        return render_template("add.html")


# TODO
@app.route("/favorite", methods=["POST"])
def favorite():

    item_id = int(request.form.get("item_id"))

    if item_id == 1:

        # ele já é favorito, então vamos desfavoritar
        return render_template("message.html", message='Item will be defavorited')
    elif item_id == 0:
        # não é favorito, então vamos favoritar
        return render_template("message.html", message='Item will be favorited')
        
    else:
        # deu algum erro, informar na tela
        return render_template("message.html", message="Internal error")

    
    # if not item_id:
    #     return render_template("message.html", message="Item couldn't be favorited")
    # else:
    #     # chenge to one in the database the is_favorite from the selected item
    #     pass
    #     return render_template("message.html", message='item added to favorites')

# TODO
@app.route("/delete", methods=["POST"])
def delete():
    item_id = request.form.get("item_id")
    
    if not item_id:
        return render_template("message.html", message="Item couldn't be deleted")
    else:
        # delete form the database the selected item, with the id we got
        pass
        return render_template("message.html", message='item deleted')






@app.route("/account", methods=["POST", "GET"])
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
def currency():
    # change currency in the database
    if request.method == "POST":



        return render_template("message.html", message="Currency changed")
    

    else: #GET
        return render_template("currency.html", currencies=CURRENCIES)


@app.route("/edit", methods = ["POST", "GET"])
def change():
    # change  infos in the database for that user
    if request.method == "POST":

        item_brand = request.form.get("brand")
        item_name = request.form.get("name")
        item_price = request.form.get("price")
        item_infos = request.form.get("item_infos")
        item_tax = request.form.get("has_tax")
        item_link = request.form.get("item_link")

        # UDPATE IN DATABASE

        return redirect("/list")

    else: #GET
        item_name = request.args.get("item_name")
        return render_template("edit.html", item_name=item_name)
        # return render_template("message.html", message="Infos changed")


# @app.route("/read")
# def read():
#     return render_template("read.html")


if __name__ == '__main__':
    app.run()



# flask --app app.py --debug run

# @app.route("/defavorite", methods=["POST"])
# def defavorite():

#     item_id = request.form.get("item_id")

#     if not item_id:
#         return render_template("message.html", message="Item couldn't be defavorite")
#     else:
#         # change is_Favorite to zero in database the selected item via its ID
#         pass
#         return render_template("message.html", message=f'{item_id} item defavorite')
    