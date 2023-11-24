# WishVerse
#### Video demo: https://youtu.be/biOWG7huEV4
#### Description:
My CS50's Final Project is a CRUD web application where the user can log in and build his/her shop wish list when he/she travels to the USA.
The application will automatically add the 8% tax and convert the US dollar to his/her actual currency.

This is a very personal project because on February 24, I will travel to Orlando, FL, with my family for the first time, and I want to organize and prepare myself for the trip, and how much money I will have to take with me.

Since I live in Brazil, the currency conversion for me will be from USD to BRL (_Brazilian real_), but the user will have the option to change from any to any currency as he/she likes.
The user will be able to add, update, or remove any item he wants, put the item link, price, quantity, brand and name, informations, and favorite it.

The static directory contains some images used in the application, the styles.css and the main.js.
The templates directory contains all pages of the application, i using Jinja syntax to use Python commands inside HTML files.

.flaskenv is a file that configures the flask enviroment, is required to install python-dotenv to use it.

The app.py is the main file of the project, inside it has all the routes created, all validations, and all SQL commands to do the CRUD operations (Create, Read, Update, Delete).
database.sqlite3 is the local database used.
init_db.py is the database initialization, is creates in the local database all the tables in the schema.sql file.

Procfile is the Heroku deployment file.

requirements.txt hass all the extensions needed to the correct operation of the application.