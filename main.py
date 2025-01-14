import streamlit as st
import numpy as np
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import firebase_admin
from firebase_admin import credentials
import re
import streamlit as st
from datetime import datetime
import json
import requests

USER_CREDENTIALS = {"admin": "password123"}
def signout():
    st.session_state.signed_in = False  # Explicitly set signed_in to False
    st.session_state.signedout = True  # This flag can be used to show that the user is signed out
    st.session_state.username = ''  # Clear username session state
    st.session_state.useremail = ''  # Clear email session state
    st.success('You have been signed out successfully!')
    st.session_state.signedout = False  # Reset signed-out flag to prevent multiple redirects
    st.session_state.signed_in = False  # Ensure that the user is not signed in
    st.rerun()

# Sign Up with email and password
def sign_up_with_email_and_password(email, password, username=None, return_secure_token=True):
    try:
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": return_secure_token
        }
        if username:
            payload["displayName"] = username
        payload = json.dumps(payload)
        r = requests.post(rest_api_url, params={"key": "AIzaSyAdgvM_-wj2IaC8gob-LGXfvuyaw6fRkjM"}, data=payload)
        
        if r.status_code == 200:
            st.success("Account Created! You can now sign in.")
            return r.json()['email']
        elif r.status_code == 400:
            error_message = r.json().get('error', {}).get('message')
            if 'EMAIL_EXISTS' in error_message:
                st.warning('This email address is already in use. Please use a different email address.')
            else:
                st.warning(f'Error: {error_message}')
        else:
            st.warning(r.json())
    except Exception as e:
        st.warning(f'Signup failed: {e}')


# Sign In with email and password
def sign_in_with_email_and_password(email=None, password=None, return_secure_token=True):
    rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    try:
        payload = {
            "returnSecureToken": return_secure_token,
            "email": email,
            "password": password
        }
        payload = json.dumps(payload)
        r = requests.post(rest_api_url, params={"key": "AIzaSyAdgvM_-wj2IaC8gob-LGXfvuyaw6fRkjM"}, data=payload)
        if r.status_code == 200:
            data = r.json()
            user_info = {
                'email': data['email'],
                'username': data.get('displayName')
            }
            st.session_state.signedout = False
            st.session_state.username = user_info['username']
            st.session_state.useremail = user_info['email']
            st.success(f"Welcome {st.session_state.username}!")
            # Now, trigger a rerun by setting a flag
            st.session_state.signed_in = True
        else:
            error_message = r.json().get('error', {}).get('message', 'Unknown error')
            st.error(f"Sign-in failed: {error_message}")
    except Exception as e:
        st.warning(f'Signin failed: {e}')

# Password Reset Function
def reset_password(email):
    try:
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        payload = {
            "email": email,
            "requestType": "PASSWORD_RESET"
        }
        payload = json.dumps(payload)
        r = requests.post(rest_api_url, params={"key": "AIzaSyAdgvM_-wj2IaC8gob-LGXfvuyaw6fRkjM"}, data=payload)
        if r.status_code == 200:
            return True, "Reset email Sent"
        else:
            error_message = r.json().get('error', {}).get('message')
            return False, error_message
    except Exception as e:
        return False, str(e)

# Function to handle password reset (forgot password)
def forget_password():
    email = st.text_input('Enter your email for password reset', key="reset_email")
    if st.button('Send Password Reset Email'):
        if email:
            success, message = reset_password(email)
            if success:
                st.success(message)
            else:
                st.error(f'Error: {message}')
        else:
            st.warning('Please enter your email address.')

def load_css():
    with open("frontend/styles.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def create_connection():
    conn = sqlite3.connect("store.db")
    return conn

def initialize_database():
    conn = create_connection()
    cursor = conn.cursor()

    # Create products table
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        item TEXT,
        srp REAL,
        dealer_price REAL
    )''')

    # Create sales table
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

    # Insert product data if not already inserted
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ("Premium IceCream", "Regular Gallon", 560, 460),
            ("Premium IceCream", "Regular 1.5L", 270, 230),
            ("Premium IceCream", "Regular 750ml", 155, 135),
            ("Supreme", "Supreme Gallon", 610, 480),
            ("Supreme", "Supreme 1.5L", 300, 250),
            ("Supreme", "Supreme 750ml", 185, 160),
            ("Others", "Sugar cone", 40, 25),
            ("Others", "Wafer Cone", 40, 25),
            ("Others", "Styro", 30, 42),
            ("Novelty", "Festive Cone", 22, 20),
            ("Novelty", "Festive Stick", 22, 20),
            ("Novelty", "Festive Cup", 30, 26),
            ("Novelty", "Dluxe Bar", 45, 40),
            ("Novelty", "Icy Pop", 10, 9),
            ("Novelty", "Vanilla Crunch", 25, 22),
            ("Novelty", "Party Cup", 15, 13),
            ("Novelty", "Sundae", 20, 18),
            ("Novelty", "Pint (reg)", 75, 67),
            ("Novelty", "Pint (S)", 95, 80),
            ("Novelty", "Café Mocha (1.5L)", 260, 240),
            ("Novelty", "Café Mocha (750ml)", 145, 135),
            ("Novelty", "Cookies & Cream (1.5L)", 260, 240),
            ("Novelty", "Cookies & Cream (750ml)", 145, 135),
        ]
        cursor.executemany("INSERT INTO products (category, item, srp, dealer_price) VALUES (?, ?, ?, ?)", products)

    conn.commit()
    conn.close()

def add_sale(product_name, quantity, date):
    conn = create_connection()
    cursor = conn.cursor()

    # Get the product_id for the selected product_name
    cursor.execute("SELECT id FROM products WHERE item = ?", (product_name,))
    product_id = cursor.fetchone()[0]

    # Calculate total sales and profit
    product_data = cursor.execute("SELECT srp, dealer_price FROM products WHERE id = ?", (product_id,)).fetchone()
    srp, dealer_price = product_data
    total_sales = quantity * srp
    total_profit = quantity * (srp - dealer_price)

    # Insert the sale into the sales table
    cursor.execute('''
        INSERT INTO sales (product_id, quantity, total_sales, total_profit, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (product_id, quantity, total_sales, total_profit, date))

    conn.commit()
    conn.close()
    st.success("Sale added successfully!")

# Function to edit an existing sale
def edit_sale(sale_id, new_quantity, new_date):
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch the sale's current data
    cursor.execute("SELECT product_id, quantity, total_sales, total_profit FROM sales WHERE id = ?", (sale_id,))
    sale_data = cursor.fetchone()

    if sale_data:
        product_id, old_quantity, old_total_sales, old_total_profit = sale_data

        # Calculate new total sales and profit
        product_data = cursor.execute("SELECT srp, dealer_price FROM products WHERE id = ?", (product_id,)).fetchone()
        srp, dealer_price = product_data
        new_total_sales = new_quantity * srp
        new_total_profit = new_quantity * (srp - dealer_price)

        # Update the sale record with the new quantity and calculated values
        cursor.execute('''
            UPDATE sales
            SET quantity = ?, total_sales = ?, total_profit = ?, date = ?
            WHERE id = ?
        ''', (new_quantity, new_total_sales, new_total_profit, new_date, sale_id))

        conn.commit()
        conn.close()
        st.success("Sale updated successfully!")
    else:
        st.error("Sale ID not found!")

# Function to delete a sale
def delete_sale(sale_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Check if the sale exists
    cursor.execute("SELECT id FROM sales WHERE id = ?", (sale_id,))
    sale_data = cursor.fetchone()

    if sale_data:
        # Delete the sale from the sales table
        cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        conn.commit()
        conn.close()
        st.success("Sale deleted successfully!")
    else:
        st.error("Sale ID not found!")

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

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])

    return df

def view_sales_by_date_range():
    st.subheader("View Sales Report by Date Range")

    # Let the user select a date range
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if start_date > end_date:
        st.error("Start date must be before end date.")
        return

    # Fetch the filtered sales data from the database
    conn = create_connection()
    query = '''
    SELECT sales.id, products.category, products.item, sales.quantity, sales.total_sales, sales.total_profit, sales.date
    FROM sales
    JOIN products ON sales.product_id = products.id
    WHERE sales.date BETWEEN ? AND ?
    '''
    sales = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()

    if sales.empty:
        st.info("No sales data available for the selected date range.")
    else:
        # Display the filtered sales data
        st.dataframe(sales)

        # Option to export the filtered sales data to Excel
        if st.button("Export to Excel"):
            try:
                # Define file name for the report
                file_name = f'data/sales_report_{start_date}_{end_date}.xlsx'

                # Create an Excel writer with the xlsxwriter engine
                with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
                    # Write the filtered sales data to the Excel file
                    sales.to_excel(writer, sheet_name='Sales Report', index=False)

                    # Format columns in the sheet (optional)
                    workbook = writer.book
                    worksheet = writer.sheets['Sales Report']
                    format1 = workbook.add_format({'num_format': '#,##0'})
                    worksheet.set_column('B:B', 15, format1)  # Item column
                    worksheet.set_column('C:C', 12, format1)  # Date column
                    worksheet.set_column('D:D', 12, format1)  # Sold Quantity column
                    worksheet.set_column('E:E', 12, format1)  # Total Sales column
                    worksheet.set_column('F:F', 12, format1)  # Total Profit column

                st.success(f"Excel file '{file_name}' has been generated successfully.")
            except Exception as e:
                st.error(f"Error during export: {e}")

def view_sales_by_date():
    # Get the sales data grouped by date
    sales_data = get_sales()

    # Group the sales data by date
    sales_by_date = sales_data.groupby('date')

    # Let the user select a date
    selected_date = st.selectbox("Select Date", sales_by_date.groups.keys())

    # Display the sales data for the selected date
    st.subheader(f"Sales for {selected_date}")
    st.dataframe(sales_by_date.get_group(selected_date))

def view_insights():
    # Get the sales data grouped by date
    sales_data = get_sales()

    # Check if sales_data is empty
    if sales_data.empty:
        st.info("No sales records available for insights.")
        return

    # Ensure 'total_profit' and 'total_sales' are numeric, forcing errors to NaN
    sales_data["total_profit"] = pd.to_numeric(sales_data["total_profit"], errors='coerce')
    sales_data["total_sales"] = pd.to_numeric(sales_data["total_sales"], errors='coerce')

    # Remove any rows where 'total_profit' or 'total_sales' is NaN
    sales_data = sales_data.dropna(subset=["total_profit", "total_sales"])

    # Now calculate total sales and profit
    total_sales = sales_data["total_sales"].sum()
    total_profit = sales_data["total_profit"].sum()

    # Display total sales and profit
    st.metric("Total Sales", f"₱{total_sales:,.2f}")
    st.metric("Total Profit", f"₱{total_profit:,.2f}")

    # Sales by category (Bar chart)
    category_sales = sales_data.groupby("category")["total_sales"].sum()
    st.subheader("Sales by Category (Bar Chart)")
    st.bar_chart(category_sales)

    # Sales distribution by category (Pie chart)
    st.subheader("Sales Distribution by Category (Pie Chart)")
    category_sales_pie = category_sales.reset_index()
    fig, ax = plt.subplots()
    ax.pie(category_sales_pie["total_sales"], labels=category_sales_pie["category"], autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3", len(category_sales_pie)))
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

    # Sales over time (Line Chart)
    st.subheader("Sales Over Time (Line Chart)")
    sales_data_by_date = sales_data.groupby("date")["total_sales"].sum()
    st.line_chart(sales_data_by_date)

    # Profit by product (Bar Chart)
    st.subheader("Profit by Product (Bar Chart)")
    product_profit = sales_data.groupby("item")["total_profit"].sum().sort_values(ascending=False)
    st.bar_chart(product_profit)

    # Sales quantity by category (Bar Chart)
    st.subheader("Sales Quantity by Category (Bar Chart)")
    category_quantity = sales_data.groupby("category")["quantity"].sum()
    st.bar_chart(category_quantity)

    # Optionally, you could include more detailed visualizations such as:
    # - Heatmaps
    # - Scatter plots (e.g., sales vs. quantity)
    # - Additional insights such as average order size per category or per product


def export_to_excel():
    try:
        # Fetch sales data with relevant details
        sales = get_sales()
        
        if sales.empty:
            st.warning("No sales data available to export.")
            return
        
        # No aggregation is done, just use the raw sales data with the necessary columns
        sales = sales[['item', 'date', 'quantity', 'total_sales', 'total_profit']]

        # Create a BytesIO buffer to export the file
        buffer = BytesIO()

        # Create an Excel writer with the xlsxwriter engine
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Write the raw sales data to the Excel file
            sales.to_excel(writer, sheet_name='Sales Report', index=False)

            # Access the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Sales Report']

            # Format columns in the sheet (optional)
            format1 = workbook.add_format({'num_format': '#,##0'})
            worksheet.set_column('B:B', 15, format1)  # Item column
            worksheet.set_column('C:C', 12, format1)  # Date column
            worksheet.set_column('D:D', 12, format1)  # Sold Quantity column
            worksheet.set_column('E:E', 12, format1)  # Total Sales column
            worksheet.set_column('F:F', 12, format1)  # Total Profit column

        buffer.seek(0)

        # Provide a download link to the user
        st.download_button(
            label="Download Sales Report as Excel",
            data=buffer,
            file_name="sales_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Excel file 'sales_report.xlsx' has been generated successfully.")

    except Exception as e:
        st.error(f"Error during export: {e}")
# Call the export function in your main function
def main():
    st.set_page_config(page_title="Inventory Dashboard", layout="wide")
    st.title("🍧 Wiggies Management System")

    if "signedout" not in st.session_state:
        st.session_state.signedout = False
    if "signed_in" not in st.session_state:
        st.session_state.signed_in = False

    if not st.session_state.signedout and not st.session_state.signed_in:
        menu = ["Sign In", "Sign Up", "Forgot Password"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Sign In":
            st.subheader("🔑 Sign In")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Sign In"):
                sign_in_with_email_and_password(email=email, password=password)
                
                # If successfully signed in, rerun to refresh the state
                if st.session_state.get("signed_in", False):
                    st.rerun()  # It will rerun the app after sign-in

        elif choice == "Sign Up":
            st.subheader("🔐 Sign Up")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            username = st.text_input("Username")
            if st.button("Sign Up"):
                sign_up_with_email_and_password(email=email, password=password, username=username)
                st.success("Account Created! You can now sign in.")

        elif choice == "Forgot Password":
            st.subheader("🔒 Reset Password")
            forget_password()  # Call the forget password function
    
    elif st.session_state.signed_in:
        st.title("Wiggies Management System")
        # Load CSS for background image
        load_css()

        # Sidebar for navigation
        menu = ["Add Sale", "Edit Sale", "View Sales", "View Sales by Date Range", "View Insights", "Export to Excel", "Delete Sale", "Sign Out"]
        choice = st.sidebar.selectbox("Select an option", menu)

        if choice == "Add Sale":
            st.subheader("Add a Sale")
            product_name = st.selectbox("Select Product", get_products()['item'].tolist())
            quantity = st.number_input("Quantity", min_value=1, value=1)
            date = st.date_input("Date of Sale")
            if st.button("Add Sale"):
                add_sale(product_name, quantity, date)

        elif choice == "Edit Sale":
            st.subheader("Edit an Existing Sale")
            sale_id = st.number_input("Sale ID", min_value=1)
            new_quantity = st.number_input("New Quantity", min_value=1)
            new_date = st.date_input("New Date of Sale")
            if st.button("Update Sale"):
                edit_sale(sale_id, new_quantity, new_date)

        elif choice == "View Sales":
            st.subheader("View Sales Records")
            sales_data = get_sales()
            st.dataframe(sales_data)

        elif choice == "View Sales by Date Range":
            view_sales_by_date_range()

        elif choice == "View Insights":
            view_insights()

        elif choice == "Export to Excel":
            export_to_excel()

        elif choice == "Delete Sale":
            st.subheader("Delete a Sale")
            sale_id = st.number_input("Enter Sale ID to Delete", min_value=1)
            if st.button("Delete Sale"):
                delete_sale(sale_id)
        
        elif choice == "Sign Out":
            signout()
            st.rerun()

if __name__ == '__main__':
    initialize_database()
    main()