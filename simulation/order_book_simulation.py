# order_book_simulation.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Title of the app
st.title("📈 Order Book Simulation")

# Description
st.markdown("""
This interactive application visualizes the simulated order book data generated by our `IntegratedDataGenerator`. 
Choose a time step to see the state of the order book, including multiple levels of bids and asks.
""")

# File uploader to allow users to upload their simulation CSV
uploaded_file = st.file_uploader("Upload Simulation CSV", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file into a DataFrame
    df = pd.read_csv(uploaded_file)
    
    # Display the first few rows
    st.subheader("Simulation Data Preview")
    st.dataframe(df.head())

    # Ensure 'Time' column is sorted
    df = df.sort_values(by='Time').reset_index(drop=True)
    
    # Slider to select the time step
    min_time = float(df['Time'].min())
    max_time = float(df['Time'].max())
    step = (max_time - min_time) / len(df)  # Adjust step based on data density

    selected_time = st.slider(
        "Select Time Step",
        min_value=min_time,
        max_value=max_time,
        value=min_time,
        step=step
    )

    # Find the nearest time step
    nearest_idx = (df['Time'] - selected_time).abs().idxmin()
    current_data = df.loc[nearest_idx]

    # Extract bids and asks
    bid_prices = []
    bid_sizes = []
    ask_prices = []
    ask_sizes = []
    depth_levels = 5  # Adjust based on your simulation

    for i in range(1, depth_levels + 1):
        bid_price = current_data.get(f'BidPrice_{i}')
        bid_size = current_data.get(f'BidSize_{i}')
        ask_price = current_data.get(f'AskPrice_{i}')
        ask_size = current_data.get(f'AskSize_{i}')

        if pd.notna(bid_price) and pd.notna(bid_size):
            bid_prices.append(bid_price)
            bid_sizes.append(bid_size)
        if pd.notna(ask_price) and pd.notna(ask_size):
            ask_prices.append(ask_price)
            ask_sizes.append(ask_size)

    # Create a Plotly figure with two subplots for bids and asks
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Bids", "Asks"))

    # Plot Bids with Hover Info
    fig.add_trace(
        go.Bar(
            x=bid_sizes,
            y=bid_prices,
            orientation='h',
            name='Bids',
            marker=dict(color='green'),
            hoverinfo='x+y',
            hovertemplate='Price: $%{y}<br>Volume: %{x}<extra></extra>'
        ),
        row=1, col=1
    )

    # Plot Asks with Hover Info
    fig.add_trace(
        go.Bar(
            x=ask_sizes,
            y=ask_prices,
            orientation='h',
            name='Asks',
            marker=dict(color='red'),
            hoverinfo='x+y',
            hovertemplate='Price: $%{y}<br>Volume: %{x}<extra></extra>'
        ),
        row=1, col=2
    )

    # Update layout
    fig.update_layout(
        title_text=f"Order Book at Time: {current_data['Time']:.4f}",
        height=600,
        showlegend=False
    )

    # Update axes titles
    fig.update_xaxes(title_text="Volume", row=1, col=1)
    fig.update_xaxes(title_text="Volume", row=1, col=2)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=2)

    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

    # Display Bid-Ask Spread
    bid_ask_spread = current_data['BidAskSpread']
    st.subheader("Bid-Ask Spread")
    st.metric(label="Spread", value=f"${bid_ask_spread:.2f}")

    # Optional: Display additional information
    st.subheader("Additional Information")
    st.write(f"**Time:** {current_data['Time']}")
    st.write(f"**Price:** ${current_data['Price']:.2f}")
    if pd.notna(current_data['Variance']):
        st.write(f"**Variance:** {current_data['Variance']:.4f}")
else:
    st.warning("Please upload a simulation CSV file to visualize the order book.")
