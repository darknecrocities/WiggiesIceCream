import sqlite3
import pandas as pd

def create_connection():
    return sqlite3.connect("store.db")

def initialize_database():
    conn = create_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        item TEXT,
        srp REAL,
        dealer_price REAL
    )''')

    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        total_sales REAL,
        total_profit REAL,
        date TEXT,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')

    # Insert initial products
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ("Premium IceCream", "Regular Gallon", 560, 460),
            # (Add remaining products here)
        ]
        cursor.executemany("INSERT INTO products (category, item, srp, dealer_price) VALUES (?, ?, ?, ?)", products)

    conn.commit()
    conn.close()

def add_sale(product_name, quantity, date):
    conn = create_connection()
    cursor = conn.cursor()
    product_data = cursor.execute("SELECT id, srp, dealer_price FROM products WHERE item = ?", (product_name,)).fetchone()
    product_id, srp, dealer_price = product_data
    total_sales = quantity * srp
    total_profit = quantity * (srp - dealer_price)
    cursor.execute('INSERT INTO sales (product_id, quantity, total_sales, total_profit, date) VALUES (?, ?, ?, ?, ?)', (product_id, quantity, total_sales, total_profit, date))
    conn.commit()
    conn.close()

def edit_sale(sale_id, new_quantity, new_date):
    conn = create_connection()
    cursor = conn.cursor()
    sale_data = cursor.execute("SELECT product_id FROM sales WHERE id = ?", (sale_id,)).fetchone()
    product_id = sale_data[0]
    product_data = cursor.execute("SELECT srp, dealer_price FROM products WHERE id = ?", (product_id,)).fetchone()
    srp, dealer_price = product_data
    new_total_sales = new_quantity * srp
    new_total_profit = new_quantity * (srp - dealer_price)
    cursor.execute('UPDATE sales SET quantity = ?, total_sales = ?, total_profit = ?, date = ? WHERE id = ?', (new_quantity, new_total_sales, new_total_profit, new_date, sale_id))
    conn.commit()
    conn.close()

def delete_sale(sale_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
    conn.commit()
    conn.close()

def get_products():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df

def get_sales():
    conn = create_connection()
    query = '''
    SELECT sales.id, products.category, products.item, sales.quantity, sales.total_sales, sales.total_profit, sales.date
    FROM sales
    JOIN products ON sales.product_id = products.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
