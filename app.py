from flask import Flask, render_template, request, redirect
# from cs50 import SQL
import sqlite3

# from flask_session import Session

app = Flask(__name__)

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

@app.route("/list")
def list():

    session = {}
    session["user_id"] = 1
    session["user_name"] = "FelipeDH"

    if session["user_id"]:
        return render_template("list.html", session=session)
    else:
        return redirect("/")

# TODO
@app.route("/add")
def add():

    session = {}
    session["user_id"] = 1
    session["user_name"] = "FelipeDH"

    if session["user_id"]:
        return render_template("add.html", session=session)
    else:
        return redirect("/")
    # return render_template("add.html")


# TODO
@app.route("/delete", methods=['POST'])
def delete():
    return render_template("error.html", error='item deleted')


# TODO
@app.route("/favorite", methods=["POST", "GET"])
def favorite():
    return render_template("error.html", error='item added to favorites')


# TODO
@app.route("/defavorite", methods=["POST", "GET"])
def defavorite():
    return render_template("error.html", error='item removed from favorites')



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")

        return render_template("login.html")
        

    else: # GET
        return render_template("login.html")

@app.route("/logout")
def logout():
    return redirect("/")


@app.route("/account")
def account():
    return redirect("/")

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
            return render_template("error.html", error="Currency not valid, please choose one in the select field!")
        else:
            return render_template("error.html", error="Currency valid!")

        


    # GET
    else:
        return render_template("register.html", currencies=CURRENCIES)
    
    



if __name__ == '__main__':
    app.run()

# flask --app app.py --debug run