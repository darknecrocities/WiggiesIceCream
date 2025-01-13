import sqlite3
import pandas as pd
import streamlit as st

# Database Setup
def init_db():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Premium_IceCream (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        item TEXT,
        srp REAL,
        dealer_price REAL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Novelty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        srp REAL,
        dealer_price REAL
    )""")

    conn.commit()
    conn.close()

# Populate the database with initial data
def populate_db():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    # Premium IceCream Data
    premium_data = [
        ("Regular", "Gallon", 560, 460),
        ("Regular", "1.5L", 270, 230),
        ("Regular", "750ml", 155, 135),
        ("Supreme", "Gallon", 610, 480),
        ("Supreme", "1.5L", 300, 250),
        ("Supreme", "750ml", 185, 160),
        ("Others", "Sugar cone", 40, 25),
        ("Others", "Wafer Cone", 40, 25),
        ("Others", "Styro", 30, 42),
    ]

    novelty_data = [
        ("Festive Cone", 22, 20),
        ("Festive Stick", 22, 20),
        ("Festive Cup", 30, 26),
        ("Dluxe Bar", 45, 40),
        ("Icy Pop", 10, 9),
        ("Vanilla Crunch", 25, 22),
        ("Party Cup", 15, 13),
        ("Sundae", 20, 18),
        ("Pint (reg)", 75, 67),
        ("Pint (S)", 95, 80),
        ("Café Mocha (1.5L)", 260, 240),
        ("Café Mocha (750ml)", 145, 135),
        ("Cookies & Cream (1.5L)", 260, 240),
        ("Cookies & Cream (750ml)", 145, 135),
    ]

    cursor.executemany("INSERT INTO Premium_IceCream (category, item, srp, dealer_price) VALUES (?, ?, ?, ?)", premium_data)
    cursor.executemany("INSERT INTO Novelty (item, srp, dealer_price) VALUES (?, ?, ?)", novelty_data)

    conn.commit()
    conn.close()

# Export to CSV
def export_to_csv():
    conn = sqlite3.connect("products.db")

    premium_df = pd.read_sql_query("SELECT * FROM Premium_IceCream", conn)
    novelty_df = pd.read_sql_query("SELECT * FROM Novelty", conn)

    premium_df.to_csv("Premium_IceCream.csv", index=False)
    novelty_df.to_csv("Novelty.csv", index=False)

    conn.close()

# Streamlit App
def main():
    st.title("Product Management System")

    menu = ["View Products", "Add Product", "Export Data"]
    choice = st.sidebar.selectbox("Menu", menu)

    conn = sqlite3.connect("products.db")

    if choice == "View Products":
        st.subheader("Premium IceCream")
        premium_df = pd.read_sql_query("SELECT * FROM Premium_IceCream", conn)
        st.dataframe(premium_df)

        st.subheader("Novelty")
        novelty_df = pd.read_sql_query("SELECT * FROM Novelty", conn)
        st.dataframe(novelty_df)

    elif choice == "Add Product":
        st.subheader("Add a New Product")
        category = st.selectbox("Category", ["Premium IceCream", "Novelty"])

        if category == "Premium IceCream":
            with st.form("add_premium_form"):
                category_input = st.text_input("Category")
                item = st.text_input("Item")
                srp = st.number_input("SRP", min_value=0.0, step=1.0)
                dealer_price = st.number_input("Dealer's Price", min_value=0.0, step=1.0)
                submit = st.form_submit_button("Add Product")

                if submit:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Premium_IceCream (category, item, srp, dealer_price) VALUES (?, ?, ?, ?)",
                                   (category_input, item, srp, dealer_price))
                    conn.commit()
                    st.success("Product added successfully!")

        elif category == "Novelty":
            with st.form("add_novelty_form"):
                item = st.text_input("Item")
                srp = st.number_input("SRP", min_value=0.0, step=1.0)
                dealer_price = st.number_input("Dealer's Price", min_value=0.0, step=1.0)
                submit = st.form_submit_button("Add Product")

                if submit:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Novelty (item, srp, dealer_price) VALUES (?, ?, ?)",
                                   (item, srp, dealer_price))
                    conn.commit()
                    st.success("Product added successfully!")

    elif choice == "Export Data":
        export_to_csv()
        st.success("Data exported successfully to CSV files!")

    conn.close()

if __name__ == "__main__":
    init_db()
    populate_db()
    main()
