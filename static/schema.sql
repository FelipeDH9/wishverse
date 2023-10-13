CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    lastname TEXT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL,
    github_username TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    brand TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    has_tax INTEGER DEFAULT 1,
    is_favorite INTEGER DEFAULT 0, 
    informations TEXT,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS products_info (
    id_product INTEGER,
    link TEXT,
    price REAL NOT NULL,
    FOREIGN KEY(id_product) REFERENCES products(id)
);

