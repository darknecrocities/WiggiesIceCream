# utils.py
import csv
from db import get_connection

def export_customers_to_csv(file_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    conn.close()

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Email", "Phone"])
        writer.writerows(customers)

def export_inventory_to_csv(file_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Inventory")
    inventory = cursor.fetchall()
    conn.close()

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Item Name", "Quantity", "Price"])
        writer.writerows(inventory)
