import sqlite3

def init_db():
    connection = sqlite3.connect("database.sqlite3")


    with open("schema.sql") as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    connection.commit()
    connection.close()

init_db()
