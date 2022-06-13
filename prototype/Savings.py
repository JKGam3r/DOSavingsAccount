import os # To find the path of the .db file

from LogIn import *
from CreateAccount import *
from RecoverAccount import *

# Routing number of this "bank"
routing_number = "123456789"

# Used for .exe file   |   Source: https://pythonprogramming.altervista.org/auto-py-to-exe-only-one-file-with-images-for-our-python-apps/
def resource_path2(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Represents the database
path = resource_path2("bankdb.db")
con = sqlite3.connect(path)
cursor = con.cursor()

# Contains methods that control the general flow of the program - think of a better name
class UserGuide:
    def __init__(self):
        self.account_ID = -1

        self.actions = [
            'BALANCE',
            'DEPOSIT',
            'TRANSFER',
            'REMOVE',
            'ALERTS',
            'DELETE',
            'OUT'
        ]

    # Keeps running through code until a valid account ID is found or the user quits
    def start_prompt(self):
        # Keep iterating until a valid user account_ID is found
        while self.account_ID == -1:
            # Ask if user is creating a new account or signing in
            valid_response = False
            while not valid_response:
                print("Type 'L' (no quotes) and Enter to Log In")
                print("Type 'C' (no quotes) and Enter to Create a New Account")
                print("Type 'R' (no quotes) and Enter to Recover an Account")
                print("Type 'Q' or 'Quit' (no quotes) and Enter to Quit")
                initial_prompt = input()
                upper_prompt = initial_prompt.upper()
                if upper_prompt == 'L':
                    valid_response = True
                elif upper_prompt == 'C':
                    valid_response = True
                elif upper_prompt == 'R':
                    valid_response = True
                elif upper_prompt == 'Q' or upper_prompt == 'QUIT':
                    quit()
                else:
                    print("INVALID RESPONSE")

            if upper_prompt == 'L':
                sign_in_obj = SignIn(cursor)
                self.account_ID = sign_in_obj.requestSignIn()  # -1 if user not found
            elif upper_prompt == 'C':
                create_account_obj = AccountCreator(cursor, con, routing_number)
                self.account_ID = create_account_obj.create_new_account()
            elif upper_prompt == 'R': # not currently working due to limitations/ security issues
                recover_account_obj = AccountRecover(cursor, con)
                # In the finished project, the account_ID should not be set, but instead call this prompt again
                self.account_ID = recover_account_obj.recover_account()

            # Something (not specified) occurred preventing a user from being found
            if self.account_ID == -1:
                print("Error.  Please try again.")

        self.display_options()

    def display_options(self):
        # Keep this variable true until delete account or signing out
        still_active = True

        while still_active:
            print("Actions:")
            print(f"\tType '{self.actions[0]}' (no quotes) to view the current balance in your account.")
            print(f"\tType '{self.actions[1]}' (no quotes) to add money to your account.")
            print(f"\tType '{self.actions[2]}' (no quotes) to transfer money to another account.")
            print(f"\tType '{self.actions[3]}' (no quotes) to remove funds from your account.")
            print(f"\tType '{self.actions[4]}' (no quotes) to view alerts for your account.")
            print(f"\tType '{self.actions[5]}' (no quotes) to delete your account.")
            print(f"\tType '{self.actions[6]}' (no quotes) to sign out of your account.")
            response = input("Your response: ").upper()

            if response == self.actions[0]:  # Balance
                print(cursor.execute("SELECT balance FROM data WHERE account_id = (?)", (self.account_ID,)).fetchone()[0])
            elif response == self.actions[1]:  # Deposit
                amount = input("How much would you like to deposit (please enter just a number): ")
                cursor.execute("UPDATE data SET balance = ? WHERE account_id = ?",
                               (int(amount), self.account_ID,))  # CHECK THIS PART
                con.commit()
            elif response == self.actions[2]:  # Transfer
                transfer_account_number = input("Type in the recipient's account number: ")
                transfer_amount = int(input("Type in the amount to transfer: "))

                # First find out if the account number is valid
                account = cursor.execute("SELECT account_id FROM data WHERE account_number = (?)", (transfer_account_number,)).fetchone()
                if account is None:
                    print("No account with this account number found.")
                    continue

                user_balance = cursor.execute("SELECT balance FROM data WHERE account_id = (?)", (self.account_ID,)).fetchone()[0]

                if user_balance < transfer_amount:  # not enough money in the account
                    print("Insufficient funds in your account.")
                    response = input(
                        "Would you like to transfer the rest of your balance into this account (Y/N)? ").upper()
                    if response == "Y" or response == "YES":  # Use up the rest of the user's balance (balance = 0)
                        cursor.execute("UPDATE data SET balance = 0 WHERE account_id = (?)",
                                       (self.account_ID,))  # CHECK THIS PART

                        receiver_balance = cursor.execute("SELECT balance FROM data WHERE account_id = (?)",
                                                          (transfer_account_number,)).fetchone()[0]
                        cursor.execute("UPDATE data SET balance = ? WHERE account_id = ?",
                                       (receiver_balance + user_balance, transfer_account_number))  # CHECK THIS PART
                        con.commit()

                        print("Transfer successful.")
                else:  # enough funds in this account
                    amount_left = user_balance - transfer_amount
                    cursor.execute("UPDATE data SET balance = ? WHERE account_id = ?",
                                   (amount_left, self.account_ID,))  # CHECK THIS PART

                    receiver_balance = cursor.execute("SELECT balance FROM data WHERE account_id = (?)",
                                                      (transfer_account_number,)).fetchone()[0]
                    cursor.execute("UPDATE data SET balance = ? WHERE account_id = ?",
                                   (receiver_balance + transfer_amount, transfer_account_number,))  # CHECK THIS PART

                    con.commit()

                    print("Transfer successful.")
            elif response == self.actions[3]:  # Remove
                print("Action not supported in this version.")
            elif response == self.actions[4]:  # Alerts
                print("Action not supported in this version.")
            elif response == self.actions[5]:  # Delete
                still_active = False
                print("Action not supported in this version but will stop the program.")
            # Depending on what needs to be done, this section may be more sophisticated
            elif response == self.actions[6]:  # Out
                still_active = False
                self.account_ID = -1
                self.start_prompt()

UserGuide().start_prompt()