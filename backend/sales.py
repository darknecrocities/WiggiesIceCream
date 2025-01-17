import streamlit as st
import pandas as pd
from database.database import get_sales
import pandas as pd

def view_sales_by_date_range():
    # Load your sales data (modify as needed for your file or data source)
    sales_data = pd.read_csv("sales.csv")  # Example: Replace with your actual data source
    
    # Ensure the 'date' column is in datetime format
    sales_data["date"] = pd.to_datetime(sales_data["date"])

    # Specify your date range
    start_date = pd.to_datetime(input("Enter the start date (YYYY-MM-DD): "))
    end_date = pd.to_datetime(input("Enter the end date (YYYY-MM-DD): "))

    # Filter sales data within the date range
    filtered_sales = sales_data[(sales_data["date"] >= start_date) & (sales_data["date"] <= end_date)]

    # Display the filtered sales data
    print(filtered_sales)


def view_sales_by_date():
    sales_data = get_sales()
    sales_by_date = sales_data.groupby("date")
    selected_date = st.selectbox("Select Date", sales_by_date.groups.keys())
    st.dataframe(sales_by_date.get_group(selected_date))
