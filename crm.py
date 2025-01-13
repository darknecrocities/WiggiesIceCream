# crm.py
from db import get_connection

def add_customer(name, email, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Customers (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
    conn.commit()
    conn.close()

def list_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    conn.close()
    return customers
