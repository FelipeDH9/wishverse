from flask import Flask, render_template, request, redirect

from flask_session import Session

app = Flask(__name__)

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