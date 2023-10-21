CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    lastname TEXT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL,
    currency TEXT NOT NULL,
    github_username TEXT
);


CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    brand TEXT NOT NULL,
    informations TEXT,
    has_tax INTEGER DEFAULT 1,
    is_favorite INTEGER DEFAULT 0, 
    link TEXT,
    price REAL NOT NULL
    );

CREATE TABLE IF NOT EXISTS user_products (
    user_id INTERGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTERGER NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
