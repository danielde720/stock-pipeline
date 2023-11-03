import streamlit as st
from cassandra.cluster import Cluster
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

# Connect to Cassandra
cluster = Cluster(['cassandra'], port=9042)
session = cluster.connect('stock_data')

# Define symbols
symbols = ['AAPL', 'AMZN', 'BINANCE:BTCUSDT', 'IC MARKETS:1']

# Create a placeholder graph
graph_placeholder = st.empty()

def fetch_data():
    data_frames = []  # List to hold DataFrames

    for symbol in symbols:
        # Query to fetch data
        query = f"SELECT * FROM stock WHERE symbol='{symbol}';"
        rows = session.execute(query)
        df = pd.DataFrame(list(rows))

        # Append DataFrame to list
        data_frames.append(df)

    # Concatenate all the data frames
    all_data = pd.concat(data_frames, ignore_index=True)

    return all_data

# Function to plot data
def plot_data(data):
    fig = px.line(data, x='timestamp', y='last_price', color='symbol', title='Stock Prices Over Time')

    # Update layout
    fig.update_layout(title='Stock Prices Over Time',
                      xaxis_title='Time',
                      yaxis_title='Price')

    graph_placeholder.plotly_chart(fig)
# Initial plot
all_data = fetch_data()
plot_data(all_data)

# Loop to update the plot in real time
while True:
    # Fetch new data
    new_data = fetch_data()

    # If there's new data, update the plot
    if not new_data.equals(all_data):
        all_data = new_data
        plot_data(all_data)

    # Sleep for a while before fetching data again
    time.sleep(10)  # Sleep for 10 seconds
