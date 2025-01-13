# db.py
import sqlite3

# Initialize and manage the database
def init_db():
    conn = sqlite3.connect("system.db")
    cursor = conn.cursor()

    # Create Customers table for CRM
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL
    )
    ''')

    # Create Inventory table for SCM
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
    )
    ''')

    # Create Orders table for SCM
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES Customers(id),
        FOREIGN KEY (item_id) REFERENCES Inventory(id)
    )
    ''')

    conn.commit()
    conn.close()

# Get a database connection
def get_connection():
    return sqlite3.connect("system.db")