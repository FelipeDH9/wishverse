from flask import Flask, render_template, request, redirect
from cs50 import SQL
import sqlite3

# from flask_session import Session

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# TODO
@app.route("/")
def index():
    return render_template("index.html")


# TODO
@app.route("/add")
def add():
    return render_template("add.html")


# TODO
@app.route("/delete")
def delete():
    pass