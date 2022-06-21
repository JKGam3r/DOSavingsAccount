# The entry point for the program, responsible for tying all modules/ files together
# Note: alerts and notifications are used interchangeably in this program

import platform # For getting the device name
import sqlite3 # Used for database

from SavingsDatabaseApplication.program_code.create_account import * # Used for creating a new account
from SavingsDatabaseApplication.program_code.login_account import * # Used for creating a new account
from SavingsDatabaseApplication.program_code.recover_account import * # Used for creating a new account
from SavingsDatabaseApplication.program_code.string_validator import * # Used for verifying a string only contains numbers
from SavingsDatabaseApplication.program_code.misc_functions import * # Used for formatting the date

# Routing number (bank identifier) for this hypothetical "bank"
ROUTING_NUMBER = "123456789"

# The table name for the table that contains usernames, passwords, and email addresses
CRED_TABLE = "credentials"

# The table name for the table that contains all of the data for the user's account
DATA_TABLE = "data"

# The table name for the table that contains each user's notifications
ALERTS_TABLE = "alerts"

# The requirements for a password
MIN_SPECIAL_CHARS = 1
MIN_CAPITALS = 1
MIN_NUMS = 1

# Represents database - function must be in same file as path called (not sure why)
# Used for .exe file   |   Source: https://pythonprogramming.altervista.org/auto-py-to-exe-only-one-file-with-images-for-our-python-apps/
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
path = resource_path("accounts.db")
connection = sqlite3.connect(path)
cursor = connection.cursor()

'''
# Initial file creation, just to have some entries in a table
# Create table and add some initial data
cursor.execute(f"CREATE TABLE {CRED_TABLE} (account_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT, password TEXT, email TEXT)")
cursor.execute(f"CREATE TABLE {DATA_TABLE} (account_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, account_number TEXT, routing_number TEXT, balance REAL)")
cursor.execute(f"CREATE TABLE {ALERTS_TABLE} (account_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, alerts TEXT)")

# Save
connection.commit()
'''

# The activities available to a logged-in user (account_ID will NOT be -1 in this case)
actions = [
    'BALANCE',
    'DEPOSIT',
    'TRANSFER',
    'CHANGE',
    'ALERTS',
    'DELETE',
    'OUT'
]

# Keeps running through the code until the user quits
def start_prompt():
    # The current user (represented as an ID) in the database, with -1=None (no active user)
    account_ID = -1
    # Ask for a response
    quit_program = False
    while not quit_program:
        print("Type 'L' (no quotes) and Enter to Log In.")
        print("Type 'C' (no quotes) and Enter to Create a New Account.")
        print("Type 'R' (no quotes) and Enter to Recover an Account.")
        print("Type 'Q' or 'Quit' (no quotes) and Enter to Quit.")
        response = input("Enter your response here: ").upper()
        print()

        if response == 'L':  # Logging in
            account_ID = SignIn(cursor, CRED_TABLE, ALERTS_TABLE).request_sign_in()
            if account_ID != -1: # user might have cancelled log in request
                print("Account login successful.")
                display_options(account_ID)
            else:
                print("User not logged in.")

        elif response == 'C':  # Creating a new account
            account_ID = AccountCreator(cursor, connection, ROUTING_NUMBER, CRED_TABLE, DATA_TABLE, ALERTS_TABLE, MIN_SPECIAL_CHARS, MIN_CAPITALS, MIN_NUMS).create_new_account()
            if account_ID != -1: # user might have cancelled create account request
                print("Account creation successful.")
                display_options(account_ID)
            else:
                print("Account not created.")

        elif response == 'R':  # Recovering an account
            AccountRecover(cursor, connection, CRED_TABLE, ALERTS_TABLE, MIN_SPECIAL_CHARS, MIN_CAPITALS, MIN_NUMS).recover_account()

        elif response == 'Q' or response == 'QUIT':  # Quit
            quit_program = True
            quit()

        else:
            print("Invalid response.  Please try again.")

        # Reset account ID
        account_ID = -1

# Shows the user all of the options available
def display_options(account_ID):
    # Keep this variable true until user either deletes account or signs out
    still_active = True

    # Continuously iterates until the account is deleted or signed out of
    while still_active:
        print("Actions:")
        print(f"\tType '{actions[0]}' (no quotes) to view the current balance in your account.")
        print(f"\tType '{actions[1]}' (no quotes) to add money to your account.")
        print(f"\tType '{actions[2]}' (no quotes) to transfer money to another account.")
        print(f"\tType '{actions[3]}' (no quotes) to change your username, password, or email.")
        print(f"\tType '{actions[4]}' (no quotes) to view alerts for your account.")
        print(f"\tType '{actions[5]}' (no quotes) to delete your account.")
        print(f"\tType '{actions[6]}' (no quotes) to sign out of your account.")

        still_active = carry_out_orders(input("Your response: ").upper(), account_ID)

    print()

# The actions that will result upon the user's input
# Returns False to return to the main menu (login, sign up, ect), returns True to continue the loop
def carry_out_orders(response, account_ID):
    if response == actions[0]:  # Balance
        display_balance(account_ID)
    elif response == actions[1]:  # Deposit
        deposit(account_ID)
    elif response == actions[2]:  # Transfer
        transfer(account_ID)
    elif response == actions[3]:  # Change
        change_credentials(account_ID)
    elif response == actions[4]:  # Alerts
        display_alerts(account_ID)
    elif response == actions[5]:  # Delete
        return delete_account(account_ID)
    elif response == actions[6]:  # Out
        return sign_out(account_ID)
    else:
        print("Invalid response.  Please try again.")

    return True

# Displays the user's balance
def display_balance(account_ID):
    amount = cursor.execute(f"SELECT balance FROM {DATA_TABLE} WHERE account_id = (?)", (account_ID,)).fetchone()[0]
    print(f"Balance: ${amount}")
    print()

# Deposits a designated amount into the user's account
def deposit(account_ID):
    amount = input("How much would you like to deposit (please enter just a number - decimal points allowed): $")
    if is_all_numbers(amount):
        # Set new balance
        current_amount = cursor.execute(f"SELECT balance FROM {DATA_TABLE} WHERE account_id = (?)", (account_ID,)).fetchone()[0]
        cursor.execute(f"UPDATE {DATA_TABLE} SET balance = ? WHERE account_id = ?",
                       (current_amount + float(amount), account_ID,))

        # Create a new alert
        all_alerts = cursor.execute(f"SELECT alerts FROM {ALERTS_TABLE} WHERE account_id = (?)", (account_ID,)).fetchone()[0]
        new_string = f"{format_date()} - Amount of ${amount} was added to your account.\n{all_alerts}"
        cursor.execute(f"UPDATE {ALERTS_TABLE} SET alerts = ? WHERE account_id = ?",
                       (new_string, account_ID,))

        # Save changes
        connection.commit()
    else:
        print("Please do not use any non-digit characters, except for a decimal point.")

    print()

# Transfers a specified monetary amount to another account
# The method of transferring money is very rudimentary to keep the process simple; not to mention transfers can only be made between bank accounts in the database created
def transfer(account_ID):
    # The final established amount that was transferred (None=no amount)
    amount_transferred = None

    # The other account's username (more information would be required in a professional app)
    transfer_account_username = input("Type in the recipient's account name: ")

    # Find out if the account name is valid
    account = cursor.execute(f"SELECT account_id FROM {CRED_TABLE} WHERE username = (?)", (transfer_account_username,)).fetchone()
    if account is None:
        print("No account found.")
        return

    # Now that a valid account has been found, get the account's ID
    transfer_acct_ID = account[0]

    # Make sure the transferred amount isn't to the same account
    if account_ID == transfer_acct_ID:
        print("Error: You are transferring money to your own account.")
        return

    # The monetary amount to move between accounts
    str_transfer_amount = input("Type in the amount (only numbers, decimal allowed) to transfer: $")

    # Just reset (quit by returning to the account options) if not a monetary amount
    if not is_all_numbers(str_transfer_amount):
        print("Not a valid monetary amount.")
        return

    # Convert the transfer amount to a valid balance number
    transfer_amount = float(str_transfer_amount)

    # Get the user's (sender's) and recipient's balances for future reference
    user_balance = cursor.execute(f"SELECT balance FROM {DATA_TABLE} WHERE account_id = (?)", (account_ID,)).fetchone()[0]
    recip_balance = cursor.execute(f"SELECT balance FROM {DATA_TABLE} WHERE account_id = (?)", (transfer_acct_ID,)).fetchone()[0]

    # Insufficient funds in the sender's account
    if user_balance < transfer_amount:
        # Notify user
        print("Insufficient funds in your account.")
        print(f"Transfer Amount: ${transfer_amount}\nYour Balance: ${user_balance}")

        # No funds at all, there cannot be a transfer
        if user_balance == 0:
            return

        # Keep iterating in this loop until a valid response (yes or no) is used
        valid_response = False
        while not valid_response:
            # The user's answer to the question prompt
            response = input("Would you like to transfer the rest of your balance into this account (Y/N)? ").upper()

            # Transfer the rest of the user's money to the other account
            if response == "Y" or response == "YES":
                cursor.execute(f"UPDATE {DATA_TABLE} SET balance = 0 WHERE account_id = (?)",(account_ID,))
                cursor.execute(f"UPDATE {DATA_TABLE} SET balance = ? WHERE account_id = ?",
                               (recip_balance + user_balance, transfer_acct_ID))

                amount_transferred = user_balance

                connection.commit()

                print("Transfer successful.")

                valid_response = True
            elif response == "N" or response == "NO":
                print("No funds will be transferred.")
                valid_response = True
            else:
                print("Invalid response.")

    else: # Sender account has enough money
        amount_left = user_balance - transfer_amount
        cursor.execute(f"UPDATE {DATA_TABLE} SET balance = ? WHERE account_id = ?",(amount_left, account_ID,))
        cursor.execute(f"UPDATE {DATA_TABLE} SET balance = ? WHERE account_id = ?",
                       (recip_balance + transfer_amount, transfer_acct_ID,))

        amount_transferred = transfer_amount

        connection.commit()

        print("Transfer successful.")

    # If not None, then a transfer was successfully made - add a notification
    if amount_transferred is not None: # transfer_acct_ID
        # Change the sender's alerts
        all_sender_alerts = cursor.execute(f"SELECT alerts FROM {ALERTS_TABLE} WHERE account_id = (?)", (account_ID,)).fetchone()[0]
        new_sender_string = f"{format_date()} - Sent ${amount_transferred} to account holder '{transfer_account_username}.'\n{all_sender_alerts}"
        cursor.execute(f"UPDATE {ALERTS_TABLE} SET alerts = ? WHERE account_id = ?",
                       (new_sender_string, account_ID,))

        # Change the recipient's alerts
        all_recipient_alerts = cursor.execute(f"SELECT alerts FROM {ALERTS_TABLE} WHERE account_id = (?)", (transfer_acct_ID,)).fetchone()[0]
        sender_username = cursor.execute(f"SELECT username FROM {CRED_TABLE} WHERE account_id = (?)", (account_ID,)).fetchone()[0]
        new_recipient_string = f"{format_date()} - Received ${amount_transferred} from account holder '{sender_username}.'\n{all_recipient_alerts}"
        cursor.execute(f"UPDATE {ALERTS_TABLE} SET alerts = ? WHERE account_id = ?",
                       (new_recipient_string, transfer_acct_ID,))

    print()

# Changes the user's username, password, and/ or email address
def change_credentials(account_ID):
    print("You can change your username, password, and/ or email address.")
    print("Type 1 to change your username.")
    print("Type 2 to change your password.")
    print("Type 3 to change your email address.")
    response = input("Your response: ")

    # Reuse the AccountCreator methods
    change_creds = AccountCreator(cursor, connection, ROUTING_NUMBER, CRED_TABLE, DATA_TABLE, ALERTS_TABLE, MIN_SPECIAL_CHARS, MIN_CAPITALS, MIN_NUMS)

    # The name of the credential that was changed
    name_of_val = None

    # The value of the credential to change (holds either the new username, password, or email)
    new_value = None

    # Keep iterating until a valid response
    valid_response = False
    while not valid_response:
        if response.upper() == 'CANCEL':
            print("Request cancelled.")
            return

        # All other options
        if response == '1': # Username
            name_of_val = "username"
            new_value = change_creds.create_username()
            valid_response = True
        elif response == '2': # Password
            name_of_val = "password"
            new_value = change_creds.create_password()
            valid_response = True
        elif response == '3': # Email address
            name_of_val = "email"
            new_value = change_creds.create_email(cursor.execute(f"SELECT username FROM {CRED_TABLE} WHERE account_id = (?)",(account_ID,)).fetchone()[0])
            valid_response = True
        else: # Invalid response
            print("Invalid response.")

    # Change username in the database and add to alerts
    cursor.execute(f"UPDATE {CRED_TABLE} SET {name_of_val} = ? WHERE account_id = ?", (new_value, account_ID,))
    all_alerts = cursor.execute(f"SELECT alerts FROM {ALERTS_TABLE} WHERE account_id = (?)",(account_ID,)).fetchone()[0]
    new_string = f"{format_date()} - Your {name_of_val} was changed.\n{all_alerts}"
    cursor.execute(f"UPDATE {ALERTS_TABLE} SET alerts = ? WHERE account_id = ?",(new_string, account_ID,))

    print()

# Shows all of the user's notifications (such as account creation, transfers, deposits, and username changes)
def display_alerts(account_ID):
    print(cursor.execute(f"SELECT alerts FROM {ALERTS_TABLE} WHERE account_id = (?)", (account_ID,)).fetchone()[0])
    print()

# Controls what happens when signing out
def sign_out(account_ID):
    # Add to alerts
    all_alerts = cursor.execute(f"SELECT alerts FROM {ALERTS_TABLE} WHERE account_id = (?)",
                                (account_ID,)).fetchone()[0]
    new_string = f"{format_date()} - Signed out on device {platform.node()}.\n{all_alerts}"
    cursor.execute(f"UPDATE {ALERTS_TABLE} SET alerts = ? WHERE account_id = ?",
                   (new_string, account_ID,))

    print()

    return False

# Deletes the account from the database
def delete_account(account_ID):
    # Confirm the deletion of the account
    print("Are you sure you want to delete your account?  All data will be lost.")

    # True if account deleted, false if not
    deleted_account = False

    # Keep waiting for a yes or no answer
    valid_response = False
    while not valid_response:
        response = input("Confirm (Y/N): ").upper()

        # Deletion of account confirmed
        if response == 'Y' or response == 'YES':
            print("Confirmed.  Your account is now being deleted...")

            cursor.execute(f"DELETE FROM {CRED_TABLE} WHERE account_id = (?)", (account_ID,))
            cursor.execute(f"DELETE FROM {DATA_TABLE} WHERE account_id = (?)", (account_ID,))
            cursor.execute(f"DELETE FROM {ALERTS_TABLE} WHERE account_id = (?)", (account_ID,))
            connection.commit()

            valid_response = True
            return False
        elif response == 'N' or response == 'NO': # Do NOT delete the account
            valid_response = True
            return True
        else:   # Iterate (the loop) again; invalid response --> not yes or no
            print("Invalid response.")

    print()

    return True

print("Welcome to the DO banking application.  This program displays basic functionality for\n"
      "savings accounts and databases.  For most user input, you can type 'Cancel' (no quotes)\n"
      "to get out of the current selection and return to a previous/ main page.  There are also\n"
      "default example accounts stored in the database.")

start_prompt()