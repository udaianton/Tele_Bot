import sqlite3

conn = sqlite3.connect('recipe.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Recipes;
DROP TABLE IF EXISTS RP;

CREATE TABLE Products (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
);

CREATE TABLE Recipes (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE,
    description TEXT
);

CREATE TABLE RP (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    recipe_id INTEGER,
    product_id INTEGER,
    UNIQUE(recipe_id, product_id)
);
''')

print('таблица обновлена')
conn.commit()
conn.close()