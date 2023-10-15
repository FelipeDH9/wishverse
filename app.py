from flask import Flask, render_template, request, redirect
# from cs50 import SQL
import sqlite3

from flask_session import Session

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# TODO
@app.route("/")
def index():

    session = {}
    session["user_id"] = 0
    session["user_name"] = "FelipeDH"

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
    return render_template("add.html")


# TODO
@app.route("/delete")
def delete():
    pass


@app.route("/logout")
def logout():
    return redirect("/")


@app.route("/account")
def account():
    return redirect("/")

@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        pass


    # GET
    else:
        return render_template("register.html")
    
    



if __name__ == '__main__':
    app.run()

# flask --app app.py --debug run