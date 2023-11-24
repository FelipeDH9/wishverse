# WishVerse
#### Video demo: https://youtu.be/biOWG7huEV4
#### Description:
My CS50's Final Project is a CRUD web application where the user can log in and build his/her shop wish list when he/she travels to the USA.
The application will automatically add the 8% tax and convert the US dollar to his/her actual currency.

This is a very personal project because on February 24, I will travel to Orlando, FL, with my family for the first time, and I want to organize and prepare myself for the trip, and how much money I will have to take with me.

Since I live in Brazil, the currency conversion for me will be from USD to BRL (_Brazilian real_), but the user will have the option to change from any to any currency as he/she likes.
The user will be able to add, update, or remove any item he wants, put the item link, price, quantity, brand and name, information, and favorite it.

Application usage:
Starting by signing up, the user has to provide his/her name, and last name, create a username, create a password and confirm it, provide the country, and select the currency he/she wants to convert to US dollars. If he/she has a LinkedIn and GitHub account, it can be provided for networking purposes. But these two aren't mandatory.

After that, the user will be redirected to the main page of the site, the wishlist itself, where will appear all the products he/she added.
Just click on the button or in the menu Add new Product. To add a product, the user has to provide the brand and name of the product, quantity, and price in US dollars. And can also provide product links if it has, and some additional information if, like "can be found in Walmart stores across the country".

On the list page, the program will calculate the conversion to the user-selected currency, and will automatically add the tax, using 8% for average tax. I added 2% of the safety margin in the currency conversion. I used it to ensure you won't run out of money during your trip. Better safe than sorry!

The currency can be changed anytime the user desires, by just clicking on the button and change.
The user can favorite the products, there will be 2 lists, one with only the favorite products, and another one with all the products he/she added. Both are calculated separately.

Can also edit the product, and change the brand, name, price, quantity, link, and information about it.
If you don't change anything, it will appear the message saying it.

Delete it, but has to confirm the deletion.

You can change something about your account, like your name, and last name, your password, or your GitHub or LinkedIn account.


Files structure:
The static directory contains some images used in the application, the styles.css and the main.js.
The templates directory contains all pages of the application, using Jinja syntax to use Python commands inside HTML files.

.flaskenv is a file that configures the flask environment and is required to install python-dotenv to use it.

The app.py is the main file of the project, it has all the routes created, all validations, and all SQL commands to do the CRUD operations (Create, Read, Update, Delete).
database.sqlite3 is the local database used.
init_db.py is the database initialization, is creates in the local database all the tables in the schema.sql file.

Procfile is the Heroku deployment file.

requirements.txt has all the extensions needed for the correct operation of the application.