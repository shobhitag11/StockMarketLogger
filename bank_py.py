import os
import pandas as pd
from datetime import datetime
import streamlit as st
from config import BANKS_FILE, BANK_TRANSACTIONS_FILE

# Load or initialize bank accounts CSV
def load_banks():
    if os.path.exists(BANKS_FILE):
        return pd.read_csv(BANKS_FILE)
    else:
        bank_columns = ["Bank Name", "Account Number", "Account Balance"]
        pd.DataFrame(columns=bank_columns).to_csv(BANKS_FILE, index=False)
        return pd.DataFrame(columns=bank_columns)

# Load or initialize transactions log CSV
def load_bank_transactions():
    if os.path.exists(BANK_TRANSACTIONS_FILE):
        return pd.read_csv(BANK_TRANSACTIONS_FILE)
    else:
        transaction_columns = ["Date", "From Bank", "To Bank", "Transaction Type", "Amount", "Description"]
        pd.DataFrame(columns=transaction_columns).to_csv(BANK_TRANSACTIONS_FILE, index=False)
        return pd.DataFrame(columns=transaction_columns)

# Style the transaction log dataframe
def style_transaction_log(df):
    def highlight_transaction_type(row):
        if row["Transaction Type"] == "Credit":
            return ["background-color: green; color: white" if col == "Transaction Type" else "" for col in df.columns]
        elif row["Transaction Type"] == "Debit":
            return ["background-color: red; color: white" if col == "Transaction Type" else "" for col in df.columns]
        return [""] * len(df.columns)

    def highlight_external(value):
        if value == "External":
            return "color: blue; font-weight: bold"
        return ""

    styled_df = df.style.apply(highlight_transaction_type, axis=1)
    styled_df = styled_df.applymap(highlight_external, subset=["From Bank", "To Bank"])
    return styled_df

# Save bank accounts to CSV
def save_banks(bank_df):
    bank_df.to_csv(BANKS_FILE, index=False)

# Save bank transactions to CSV
def save_transactions(transaction_df):
    transaction_df.to_csv(BANK_TRANSACTIONS_FILE, index=False)

# Bank Details UI
def bank_details():
    st.title("💰 Bank Details")

    # Load bank accounts and transactions
    banks_df = load_banks()
    transactions_df = load_bank_transactions()

    # Sidebar for debit/credit transactions
    st.sidebar.title("Transaction")

    if not banks_df.empty:
        selected_bank = st.sidebar.selectbox("Select Bank", banks_df["Bank Name"])
        transaction_type = st.sidebar.radio("Transaction Type", ("Credit", "Debit"))
        amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=0.1, key="transaction_amount")
        description = st.sidebar.text_input("Description (optional)", key="transaction_description")

        if st.sidebar.button("Submit Transaction"):
            if amount <= 0:
                st.sidebar.error("Amount must be greater than 0!")
            else:
                bank_balance = banks_df[banks_df["Bank Name"] == selected_bank]["Account Balance"].values[0]
                
                if transaction_type == "Debit" and bank_balance < amount:
                    st.sidebar.error("Insufficient balance for this debit transaction!")
                else:
                    # Update bank balance and log transaction
                    if transaction_type == "Credit":
                        banks_df.loc[banks_df["Bank Name"] == selected_bank, "Account Balance"] += amount
                        new_transaction = pd.DataFrame({
                            "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                            "From Bank": "External",
                            "To Bank": [selected_bank],
                            "Transaction Type": [transaction_type],
                            "Amount": [amount],
                            "Description": [description]
                        })
                    else:  # Debit
                        banks_df.loc[banks_df["Bank Name"] == selected_bank, "Account Balance"] -= amount
                        new_transaction = pd.DataFrame({
                            "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                            "From Bank": [selected_bank],
                            "To Bank": "External",
                            "Transaction Type": [transaction_type],
                            "Amount": [amount],
                            "Description": [description]
                        })

                    save_banks(banks_df)
                    transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
                    save_transactions(transactions_df)
                    st.sidebar.success(f"{transaction_type} of ₹{amount:,.2f} was successful for {selected_bank}")
    else:
        st.sidebar.info("No banks available. Please add a bank first.")

    # Add new bank account form
    with st.expander("➕ Add New Bank Account"):
        bank_name = st.text_input("Bank Name", key="bank_name")
        account_number = st.text_input("Account Number", key="account_number")
        initial_balance = st.number_input("Initial Balance (₹)", min_value=0.0, step=0.1, key="initial_balance")

        if st.button("Add Bank Account"):
            if bank_name and account_number and initial_balance >= 0:
                if not banks_df[banks_df['Account Number'] == account_number].empty:
                    st.error("Bank account with this number already exists!")
                else:
                    new_account = pd.DataFrame({
                        "Bank Name": [bank_name],
                        "Account Number": [account_number],
                        "Account Balance": [initial_balance]
                    })
                    banks_df = pd.concat([banks_df, new_account], ignore_index=True)
                    save_banks(banks_df)
                    st.success(f"Added bank account: {bank_name}")
            else:
                st.error("Please fill all fields correctly!")

    # Self transfer money form
    with st.expander("➔ Self Transfer Money"):
        if not banks_df.empty:
            from_bank = st.selectbox("From Bank", banks_df["Bank Name"])
            to_bank = st.selectbox("To Bank", banks_df["Bank Name"])

            if from_bank == to_bank:
                st.error("Source and destination banks cannot be the same!")
            else:
                amount = st.number_input("Amount (₹)", min_value=0.0, step=0.1, key="transfer_amount")
                description = st.text_input("Description (optional)", key="transfer_description")

                if st.button("Transfer Money"):
                    if amount <= 0:
                        st.error("Transfer amount must be greater than 0!")
                    else:
                        from_balance = banks_df[banks_df["Bank Name"] == from_bank]["Account Balance"].values[0]

                        if from_balance >= amount:
                            banks_df.loc[banks_df["Bank Name"] == from_bank, "Account Balance"] -= amount
                            banks_df.loc[banks_df["Bank Name"] == to_bank, "Account Balance"] += amount
                            save_banks(banks_df)

                            new_transaction = pd.DataFrame({
                                "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                                "From Bank": [from_bank],
                                "To Bank": [to_bank],
                                "Transaction Type": "Self",
                                "Amount": [amount],
                                "Description": [description]
                            })
                            transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
                            save_transactions(transactions_df)
                            st.success(f"Transferred ₹{amount:,.2f} from {from_bank} to {to_bank}")
                        else:
                            st.error("Insufficient balance in the source bank account!")
        else:
            st.info("Add at least two bank accounts to perform transactions.")

    # Display bank accounts
    st.subheader("Your Bank Accounts")
    if not banks_df.empty:
        st.dataframe(banks_df, use_container_width=True, hide_index=True)
    else:
        st.info("No bank accounts added yet. Use the form above to add one.")

    # Display transaction log
    st.subheader("Transaction Log")
    if not transactions_df.empty:
        st.dataframe(transactions_df.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        st.download_button(
            label="Download Transaction Log as CSV",
            data=transactions_df.to_csv(index=False),
            file_name="bank_transactions.csv",
            mime="text/csv"
        )
    else:
        st.info("No transactions logged yet.")

if __name__ == "__main__":
    bank_details()
