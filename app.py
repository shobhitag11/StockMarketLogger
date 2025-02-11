"""
Stock Portfolio Manager Application
Developer Name: Shobhit Agarwal
GitHub Profile: https://github.com/shobhitag11
Read more on: https://iamshobhitagarwal.medium.com/

Objective:
1. Configure the Streamlit page for the stock portfolio manager.
2. Load or initialize stock data from a JSON file.
3. Load or initialize transaction log data from a CSV file.
4. Provide functionality to add new stocks.
5. Log buy and sell transactions.
6. Update the stock database with buy/sell operations.
7. Filter stock data by broker.
8. Display portfolio metrics and transaction logs.
9. Provide a user interface for stock operations and bank details.

"""

import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu
from bank_py import bank_details
from config import STOCKS_FILE, CSV_FILE, TRANSACTION_LOG_FILE

# Page configuration
st.set_page_config(page_title="Stock Portfolio Manager", page_icon="📊", layout="wide")

# Custom styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px;
    }
    .metric-positive {
        color: green;
        font-weight: bold;
    }
    .metric-negative {
        color: red;
        font-weight: bold;
    }
    .metric-neutral {
        color: blue;
        font-weight: bold;
    }
    .metric-dark-green {
        color: darkgreen;
        font-weight: bold;
    }
    .metric-dark-red {
        color: darkred;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize or load stocks list from JSON
def load_stocks():
    """
    Load stocks from the JSON file if it exists, otherwise initialize with default stocks.
    """
    if os.path.exists(STOCKS_FILE):
        with open(STOCKS_FILE, 'r') as f:
            return json.load(f)
    else:
        default_stocks = {
            "stocks": [
                {"symbol": "RELIANCE", "name": "Reliance Industries Ltd"},
                {"symbol": "TCS", "name": "Tata Consultancy Services Ltd"},
                {"symbol": "INFY", "name": "Infosys Ltd"},
                {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd"},
                {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd"}
            ]
        }
        with open(STOCKS_FILE, 'w') as f:
            json.dump(default_stocks, f, indent=4)
        return default_stocks

# Save stocks to JSON file
def save_stocks(stocks_data):
    """
    Save the given stocks data to the JSON file.
    """
    with open(STOCKS_FILE, 'w') as f:
        json.dump(stocks_data, f, indent=4)

# Initialize transaction log CSV if not exists
if not os.path.exists(TRANSACTION_LOG_FILE):
    transaction_log_columns = ["Date Time", "Stock", "Action", "Quantity", "Share Price", "Total Value", "Broker"]
    pd.DataFrame(columns=transaction_log_columns).to_csv(TRANSACTION_LOG_FILE, index=False)

# Load stocks data
stocks_data = load_stocks()

# Placeholder for stock database with improved fields
data = {
    'Stock': [],
    'Broker': [],
    'Date': [],
    'Buy Quantity': [],
    'Buy Price': [],
    'Total Buy Value': [],
    'Sell Quantity': [],
    'Sell Price': [],
    'Total Sell Value': [],
    'Current Quantity': [],
    'Average Buy Price': [],
    'Total Investment': [],
    'Market Value': [],
    'Realized P/L': [],
    'Unrealized P/L': []
}
df = pd.DataFrame(data)

# Load existing data if the CSV file exists
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    df.to_csv(CSV_FILE, index=False)

# Initialize session state
if "selected_stock" not in st.session_state:
    st.session_state["selected_stock"] = "Select a stock"

if "stock_broker_mapping" not in st.session_state:
    st.session_state["stock_broker_mapping"] = {}

# Function to add new stock
def add_new_stock(symbol, name):
    """
    Add a new stock to the stocks data and save it to the JSON file.
    """
    stocks_data['stocks'].append({
        "symbol": symbol.upper(),
        "name": name
    })
    save_stocks(stocks_data)
    return True

# Function to log transactions
def log_transaction(stock_symbol, action, quantity, share_price, broker):
    """
    Log a transaction (buy/sell) to the transaction log CSV file.
    """
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_value = quantity * share_price
    log_entry = {
        "Date Time": current_datetime,
        "Stock": stock_symbol,
        "Action": action,
        "Quantity": quantity,
        "Share Price": share_price,
        "Total Value": total_value,
        "Broker": broker
    }
    # Append log to CSV
    log_df = pd.DataFrame([log_entry])
    log_df.to_csv(TRANSACTION_LOG_FILE, mode='a', header=False, index=False)

# Function to filter data by broker
def filter_by_broker():
    """
    Filter the stock data by the selected broker.
    """
    global df
    selected_broker = st.selectbox("Filter by Broker", options=["All Brokers"] + list(df["Broker"].unique()))
    if selected_broker != "All Brokers":
        filtered_df = df[df["Broker"] == selected_broker]
    else:
        filtered_df = df
    return filtered_df

# Function to update database
def update_database(stock_symbol, stock_name, quantity, share_price, action, broker):
    """
    Update the stock database with buy/sell operations and log the transaction.
    """
    global df
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Check if stock with the same broker exists
    stock_exists_with_broker = (
        (df['Stock'] == stock_symbol) & (df['Broker'] == broker)
    ).any()

    if action == "Buy":
        if stock_exists_with_broker:
            # Update existing row for the stock with the same broker
            stock_index = df[(df['Stock'] == stock_symbol) & (df['Broker'] == broker)].index[0]
            current_quantity = df.at[stock_index, 'Current Quantity']
            current_total_investment = df.at[stock_index, 'Total Investment']

            new_quantity = current_quantity + quantity
            new_total_investment = current_total_investment + (quantity * share_price)
            new_avg_price = new_total_investment / new_quantity

            df.at[stock_index, 'Date'] = current_date
            df.at[stock_index, 'Buy Quantity'] += quantity
            df.at[stock_index, 'Buy Price'] = share_price
            df.at[stock_index, 'Total Buy Value'] += quantity * share_price
            df.at[stock_index, 'Current Quantity'] = new_quantity
            df.at[stock_index, 'Average Buy Price'] = new_avg_price
            df.at[stock_index, 'Total Investment'] = new_total_investment
            df.at[stock_index, 'Market Value'] = new_quantity * share_price
            df.at[stock_index, 'Unrealized P/L'] = (
                df.at[stock_index, 'Market Value'] - df.at[stock_index, 'Total Investment']
            )
        else:
            # Add new row for the stock with the different broker
            new_entry = pd.DataFrame({
                'Stock': [stock_symbol],
                'Broker': [broker],
                'Date': [current_date],
                'Buy Quantity': [quantity],
                'Buy Price': [share_price],
                'Total Buy Value': [quantity * share_price],
                'Sell Quantity': [0],
                'Sell Price': [0],
                'Total Sell Value': [0],
                'Current Quantity': [quantity],
                'Average Buy Price': [share_price],
                'Total Investment': [quantity * share_price],
                'Market Value': [quantity * share_price],
                'Realized P/L': [0.0],
                'Unrealized P/L': [0.0]
            })
            df = pd.concat([df, new_entry], ignore_index=True)

        log_transaction(stock_symbol, action, quantity, share_price, broker)

    elif action == "Sell":
        if stock_exists_with_broker:
            # Update the row for the stock with the same broker
            stock_index = df[(df['Stock'] == stock_symbol) & (df['Broker'] == broker)].index[0]
            current_quantity = df.at[stock_index, 'Current Quantity']
            avg_buy_price = df.at[stock_index, 'Average Buy Price']

            if current_quantity >= quantity:
                realized_pl = (share_price - avg_buy_price) * quantity
                remaining_quantity = current_quantity - quantity

                df.at[stock_index, 'Date'] = current_date
                df.at[stock_index, 'Sell Quantity'] += quantity
                df.at[stock_index, 'Sell Price'] = share_price
                df.at[stock_index, 'Total Sell Value'] += quantity * share_price
                df.at[stock_index, 'Current Quantity'] = remaining_quantity
                df.at[stock_index, 'Realized P/L'] += realized_pl

                df.at[stock_index, 'Market Value'] = remaining_quantity * share_price
                df.at[stock_index, 'Unrealized P/L'] = (
                    remaining_quantity * (share_price - avg_buy_price)
                )

                df.at[stock_index, 'Total Investment'] = (
                    remaining_quantity * avg_buy_price
                )
            else:
                st.sidebar.error("Insufficient quantity to sell for the selected broker!")
                return False
        else:
            st.sidebar.error("Stock not found in your portfolio for the selected broker!")
            return False

        log_transaction(stock_symbol, action, quantity, share_price, broker)

    df.to_csv(CSV_FILE, index=False)
    st.session_state["stock_broker_mapping"][stock_symbol] = broker
    return True

def stock_operations():
    """
    Handle stock operations including adding new stocks, buying, and selling stocks.
    Display portfolio metrics and transaction logs.
    """
    global stocks_data
    st.title("📊 Stock Portfolio Manager")

    filtered_df = filter_by_broker()

    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)

    # Calculate and display portfolio metrics
    if not filtered_df.empty:
        with col1:
            total_investment = filtered_df['Total Investment'].sum()
            st.markdown(f"<span class='metric-neutral'>Total Investment: \u20b9{total_investment:,.2f}</span>", unsafe_allow_html=True)

        with col2:
            total_market_value = filtered_df['Market Value'].sum()
            market_value_class = "metric-dark-green" if total_market_value >= total_investment else "metric-dark-red"
            st.markdown(f"<span class='{market_value_class}'>Current Market Value: \u20b9{total_market_value:,.2f}</span>", unsafe_allow_html=True)

        with col3:
            total_pl = filtered_df['Realized P/L'].sum() + filtered_df['Unrealized P/L'].sum()
            pl_class = "metric-positive" if total_pl >= 0 else "metric-negative"
            st.markdown(f"<span class='{pl_class}'>Total P/L: \u20b9{total_pl:,.2f}</span>", unsafe_allow_html=True)

    # Sidebar for user inputs
    with st.sidebar:

        with st.expander("\u2795 Add New Stock"):
            new_stock_symbol = st.text_input("Stock Symbol", key="new_stock_symbol").upper()
            new_stock_name = st.text_input("Stock Name", key="new_stock_name")

            if st.button("Add Stock"):
                if new_stock_symbol and new_stock_name:
                    if any(stock["symbol"] == new_stock_symbol for stock in stocks_data["stocks"]):
                        st.error("Stock symbol already exists!")
                    else:
                        if add_new_stock(new_stock_symbol, new_stock_name):
                            st.success(f"Added {new_stock_symbol} to the stock list")
                            stocks_data = load_stocks()
                else:
                    st.error("Please enter both symbol and name")

        st.divider()

        stock_list = ["Select a stock"] + [f"{stock['symbol']} - {stock['name']}" for stock in stocks_data["stocks"]]

        selected_stock_full = st.selectbox("Choose a stock:", stock_list, help="Search and select a stock", key="selected_stock")

        if selected_stock_full != "Select a stock":
            selected_stock_symbol = selected_stock_full.split(" - ")[0]
            selected_stock_name = selected_stock_full.split(" - ")[1]
        else:
            selected_stock_symbol = "Select a stock"
            selected_stock_name = ""

        disable_inputs = selected_stock_symbol == "Select a stock"

        broker = st.radio("Select Broker", ["Zerodha", "Fyers"], index=0 if st.session_state["stock_broker_mapping"].get(selected_stock_symbol) == "Zerodha" else 1, disabled=disable_inputs)

        quantity = st.number_input("Enter Quantity", min_value=1, value=1, step=1, disabled=disable_inputs)

        share_price = st.number_input("Enter Share Price", min_value=0.0, value=0.0, step=0.1, format="%.2f", disabled=disable_inputs)

        if not disable_inputs:
            total_value = quantity * share_price
            st.write(f"**Total Value**: \u20b9{total_value:,.2f}")

        buy_col, sell_col = st.columns(2)

        with buy_col:
            if st.button("Buy", disabled=disable_inputs, use_container_width=True):
                if selected_stock_symbol != "Select a stock" and quantity > 0 and share_price > 0:
                    if update_database(selected_stock_symbol, selected_stock_name, quantity, share_price, "Buy", broker):
                        st.success(f"Bought {quantity} shares of {selected_stock_symbol} at \u20b9{share_price:,.2f} using {broker}")
                else:
                    st.error("Please fill all fields correctly")

        with sell_col:
            if st.button("Sell", disabled=disable_inputs, use_container_width=True):
                if selected_stock_symbol != "Select a stock" and quantity > 0 and share_price > 0:
                    if update_database(selected_stock_symbol, selected_stock_name, quantity, share_price, "Sell", broker):
                        st.success(f"Sold {quantity} shares of {selected_stock_symbol} at \u20b9{share_price:,.2f} using {broker}")
                else:
                    st.error("Please fill all fields correctly")

    # Main content area
    st.subheader("Your Stock Portfolio")
    if not filtered_df.empty:
        display_df = filtered_df.copy()
        numeric_columns = display_df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            display_df[col] = display_df[col].apply(lambda x: f"\u20b9{x:,.2f}" if 'Price' in col or 'Value' in col or 'P/L' in col or 'Investment' in col else f"{x:,.0f}" if 'Quantity' in col else x)

        st.dataframe(display_df.sort_values('Date', ascending=False), use_container_width=True, height=400, hide_index=True)
    else:
        st.info("Your portfolio is empty. Start by adding some stocks!")

    with st.expander("Transaction Log"):
        if os.path.exists(TRANSACTION_LOG_FILE):
            transaction_log_df = pd.read_csv(TRANSACTION_LOG_FILE)
            filtered_logs = transaction_log_df[transaction_log_df["Broker"].isin(filtered_df["Broker"].unique())]

            st.dataframe(
                filtered_logs.sort_values("Date Time", ascending=False),
                use_container_width=True,
                height=300,
                hide_index=True
            )

            st.download_button(
                label="Download Transaction Log as CSV",
                data=filtered_logs.to_csv(index=False),
                file_name="transaction_log.csv",
                mime="text/csv"
            )
        else:
            st.info("No transactions logged yet. Start by buying or selling stocks!")

def main_screen():
    """
    Main screen to navigate between stock operations and bank details.
    """
    with st.sidebar:
        selected_page = option_menu(
            "Market Menu",
            ["Stock Operations", "Bank Details"],
            icons=["pencil-square", "bank"],
            menu_icon="cast",
            default_index=0,
        )
    if selected_page == "Stock Operations":
        stock_operations()
    elif selected_page == "Bank Details":
        bank_details()

if __name__ == "__main__":
    main_screen()
