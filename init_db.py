import sqlite3

connection = sqlite3.connect("postgres://kolposefgivsfg:f55297fb1552520b77a14e2919c93e6430762fedb89aa78499140933412274d6@ec2-18-213-255-35.compute-1.amazonaws.com:5432/da2v8nmgjslig3")


with open("schema.sql") as f:
    connection.executescript(f.read())

cur = connection.cursor()

connection.commit()
connection.close()
