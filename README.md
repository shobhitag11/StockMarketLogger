# Stock Portfolio Manager

## Overview

The Stock Portfolio Manager is a web application built using Streamlit that allows users to manage their stock portfolios and bank accounts. The application provides functionalities to add new stocks, log buy and sell transactions, update stock databases, filter stock data by broker, display portfolio metrics, and manage bank details.

## Features

- **User Authentication**: Secure login and registration system to manage user access.
- **Stock Management**: Add new stocks, buy and sell stocks, and update the stock database.
- **Portfolio Metrics**: Display total investment, current market value, and total profit/loss.
- **Transaction Logging**: Log all buy and sell transactions with details.
- **Bank Management**: Add new bank accounts, perform credit/debit transactions, and transfer money between accounts.
- **Data Persistence**: Store stock data, transaction logs, and bank details in CSV and JSON files.

## Code Flow

### Main Components

1. **app.py**: The main entry point of the application. It configures the Streamlit page, loads stock data, initializes the transaction log, and provides the main screen navigation between stock operations and bank details.

2. **bank_py.py**: Handles bank-related functionalities such as loading bank accounts, logging transactions, updating bank balances, and displaying bank details.

3. **config.py**: Contains file paths for storing stock data, transaction logs, and bank details.

### Detailed Explanation

#### app.py

- **Page Configuration**: Sets up the Streamlit page with a title, icon, and layout.
- **Load Stocks**: Loads stock data from a JSON file or initializes it with default stocks if the file does not exist.
- **Save Stocks**: Saves the given stock data to the JSON file.
- **Log Transaction**: Logs buy/sell transactions to the transaction log CSV file.
- **Update Database**: Updates the stock database with buy/sell operations and logs the transaction.
- **Stock Operations**: Handles stock operations, displays portfolio metrics, and transaction logs.
- **Main Screen**: Provides navigation between stock operations and bank details.

#### bank_py.py

- **Load Banks**: Loads bank accounts from a CSV file or initializes it if the file does not exist.
- **Load Bank Transactions**: Loads bank transactions from a CSV file or initializes it if the file does not exist.
- **Save Banks**: Saves bank accounts to the CSV file.
- **Save Transactions**: Saves bank transactions to the CSV file.
- **Bank Details**: Manages bank details, including adding new bank accounts, performing credit/debit transactions, and transferring money between accounts.

#### config.py

- **File Paths**: Defines file paths for storing stock data, transaction logs, and bank details.

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:

```sh
git clone https://github.com/shobhitag11/StockMarket.git
cd StockMarket
```
2. Create a virtual environment and activate it:
```sh
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the required packages:
```sh
pip install -r requirements.txt
```

4. Start the Streamlit application:
```sh
streamlit run app.py
```
5. Open your web browser and navigate to http://localhost:8501 to access the application.

## Usage
1. **Stock Operations**: Navigate to the "Stock Operations" page to manage your stock portfolio.
2. **Bank Details**: Navigate to the "Bank Details" page to manage your bank accounts and transactions.

## License
This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Author
**Shobhit Agarwal**
GitHub: [shobhitag11](https://github.com/shobhitag11)
Medium: [iamshobhitagarwal](https://iamshobhitagarwal.medium.com/)
