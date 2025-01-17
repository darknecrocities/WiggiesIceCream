import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from database.database import get_sales

def view_insights():
    sales_data = get_sales()
    total_sales = sales_data["total_sales"].sum()
    total_profit = sales_data["total_profit"].sum()
    st.metric("Total Sales", f"₱{total_sales:,.2f}")
    st.metric("Total Profit", f"₱{total_profit:,.2f}")
    category_sales = sales_data.groupby("category")["total_sales"].sum()
    st.bar_chart(category_sales)
