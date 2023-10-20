from flask import Flask, render_template, request, redirect, session
# from cs50 import SQL
import sqlite3
import requests
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


CURRENCIES = [
            {'iso':'EUR','name': 'Euro'},
            {'iso':'BRL','name': 'Brazilian Real'},
            {'iso':'JPY','name': 'Japanese yen'},
            {'iso':'GBP','name': 'Pound sterling'}, 
            {'iso':'AUD','name': 'Australian dollar'}, 
            {'iso':'CAD','name': 'Canadian dollar'}, 
            {'iso':'CHF','name': 'Swiss franc'}, 
            {'iso':'CNH','name': 'Chinese renminbi'}, 
            {'iso':'HKD','name': 'Hong Kong dollar'}, 
            {'iso':'NZD','name': 'New Zealand dollar'}, 
            {'iso':'MXN','name': 'Mexixan peso'}
            ]

# list of currencies iso codes
CURRENCIES_ISO = [currency['iso'] for currency in CURRENCIES]


# TODO
@app.route("/")
def index():

    session = {}
    session["user_id"] = 1
    session["user_name"] = "FelipeDH"

    # if not log in, render the home page which explains what the application is
    # if not session["user_id"]:
    #     return render_template("index.html")
    
    # # if has session, than render the index which shows the users products
    # else:
    #     return render_template("list.html", session=session)

    return render_template("index.html", session=session)
    
    # if has session, than render the index which shows the users products
    # else:
    #     return render_template("list.html", session=session)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":

        # Forget any user_id
        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("message.html", message="Username must be provided")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("message.html", message="Password must be provided")
            
        # Query database for username
        # rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        # if len(rows) != 1 or not check_password_hash(
        #     rows[0]["hash"], request.form.get("password")
        # ):
            # return apology("invalid username and/or password", 403)
        pass

        # Remember which user has logged in
        # session["user_id"] = rows[0]["id"]

        # Redirect user to home page
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



@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        last_name = request.form.get("last_name")
        user_name = request.form.get("user_name")
        github = request.form.get("github")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get("country")
        currency = request.form.get("currency")
        
        # validate if currency exists
        if currency not in CURRENCIES_ISO:
            return render_template("message.html", message="Currency not valid, please choose one in the select field!")
        else:
            return render_template("message.html", message="Currency valid!")

        


    # GET
    else:
        return render_template("register.html", currencies=CURRENCIES)
    
    
@app.route("/currency", methods = ["POST", "GET"])
def currency():
    # change currency in the database
    if request.method == "POST":



        return render_template("message.html", message="Currency changed")
    

    else: #GET
        return render_template("currency.html", currencies=CURRENCIES)


@app.route("/change", methods = ["POST"])
def change():
    # change  infos in the database for that user

        return render_template("message.html", message="Infos changed")


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
    