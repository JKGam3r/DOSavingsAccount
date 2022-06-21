# Deals with logging a user into the system

import platform # For getting the device name
import pwinput # Used for password input

from SavingsDatabaseApplication.program_code.string_validator import * # Used for comparing password hashes
from SavingsDatabaseApplication.program_code.misc_functions import * # Used for formatting the date

# Outlines everything needed to sign a user into an account
class SignIn:
    # Constructor
    def __init__(self, cursor, cred_table, alerts_table):
        # Used for getting data out of the table
        self.cursor = cursor

        # Used for getting the table that contains the usernames and passwords
        self.cred_table = cred_table

        # Used for setting a new alert
        self.alerts_table = alerts_table

        # Used for cancelling the sign in request
        self.cancel_account_login = False

    # Single sign-on (SSO) authentication
    def prompt(self):
        print("You can cancel the log in process at any point by typing 'Cancel' (no quotes).")

        username = input("Username: ")
        if username.lower() == 'cancel':
            print("Request cancelled.")
            self.cancel_account_login = True
            return None, None

        password = pwinput.pwinput("Password: ")
        if password.lower() == 'cancel':
            print("Request cancelled.")
            self.cancel_account_login = True
            return None, None

        print()
        return username, password

    # Parameterized query; finds a hashed password in the database with the username
    def search(self, username):
        # The stored password in the database; will remain none if no such username in the database
        hashed_password = None

        password_obj = self.cursor.execute(f"SELECT password FROM {self.cred_table} WHERE username = (?)", (username,)).fetchone()

        # If the password object is not None, then that means a username was found in the database (with a designated password)
        if password_obj is not None:
            hashed_password = password_obj[0]

        return hashed_password

    # Return True if username+password are valid, False if the combination is invalid
    def is_valid(self, input_password, hashed_password):
        if hashed_password is not None: # return true if they match, false if password incorrect
            return compare_passwords(input_password, hashed_password)
        else: # the username was not valid
            return False

    # Wraps all of the methods in one to ask the user to sign into their account
    def request_sign_in(self):
        # returned --> stays -1 if no account found, changes to a valid account id if there is an account
        cred_id = -1

        input_username, input_password = self.prompt()

        if self.cancel_account_login:
            return cred_id

        hashed_password = self.search(input_username)
        is_valid_credentials = self.is_valid(input_password, hashed_password)

        # Change the credential ID if the username-password combination is valid
        if is_valid_credentials:
            cred_id = self.cursor.execute(f"SELECT account_id FROM {self.cred_table} WHERE username = (?)", (input_username,)).fetchone()[0]

            # Add to alerts
            all_alerts = self.cursor.execute(f"SELECT alerts FROM {self.alerts_table} WHERE account_id = (?)",
                                             (cred_id,)).fetchone()[0]
            new_string = f"{format_date()} - Signed in on device {platform.node()}.\n{all_alerts}"
            self.cursor.execute(f"UPDATE {self.alerts_table} SET alerts = ? WHERE account_id = ?",
                           (new_string, cred_id,))
        else:
            print("Username or password is incorrect.")

        print()
        return cred_id