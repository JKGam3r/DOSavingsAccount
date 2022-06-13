import pwinput # Used for passwords
import sqlite3 # Database
import random # Random account number

from PasswordManager import *

# Creates a new account; notice how there are no other variables in the constructor besides
# the cursor, con, and routing number (to help prevent from outside access)
class AccountCreator:
    def __init__(self, cursor, con, routing_number):
        # Represents the database
        self.cursor = cursor
        self.con = con

        # The routing number of the "bank"
        self.routing_number = routing_number

    # Keep asking user for a username if there already is a username that matches
    def __create_username(self):
        final_username = ""

        valid_username = False
        while not valid_username:
            typed_username = input("Type in a username: ")
            db_username = self.cursor.execute("SELECT account_id FROM sso WHERE username = (?)", (typed_username,)).fetchone()

            if db_username is None: # typed username not used yet; valid
                final_username = typed_username
                valid_username = True
            else: # username already in database
                print("Selected username already taken.  Please try again.")

        return final_username

    # Ask for a password; in this prototype, no specifications (length, capital letters, special characters, etc. are required)
    def __create_password(self):
        final_password = ""

        same_passwords = False
        while not same_passwords:
            password1 = pwinput.pwinput("Type in a password: ")
            password2 = pwinput.pwinput("Retype your password: ")

            if password1 == password2: # same password; checks out
                final_password = password1
                same_passwords = True
            else:
                print("Passwords do not match.  Please try again.")

        return final_password

    # Ask for an email
    def __create_email(self):
        final_email = ""

        print("You have the option to set a recover email --> Y for Yes, N for No")
        print("Please keep in mind that opting out will prevent any username/ password recovery.")
        selection = input("Your choice: ")

        sel_to_upper = selection.upper()
        if sel_to_upper == "Y" or sel_to_upper == "YES":
            final_email = input("Type in an email: ")

        return final_email

    # Generates a random account number (will not be based on anything); not the best way, but it works
    def __generate_account_number(self):
        unique_acct_number = False

        # Think of a better way of doing this
        while not unique_acct_number:
            current = random.randrange(10_000_000, 11_000_000)
            str_current = str(current)
            db_acct_number = self.cursor.execute("SELECT account_number FROM data WHERE account_number = (?)",
                                              (str_current,)).fetchone()

            if db_acct_number == None:
                unique_acct_number = True
                return str_current

    # Adds the values as an entry to the table
    def __add_to_database(self, username, password, email, account_number):
        salt_and_key = generatePasswordHash(password)
        storage = salt_and_key[0] + salt_and_key[1]
        self.cursor.execute("INSERT INTO sso VALUES (?, ?, ?, ?)", (None, username, storage, email, ))
        saved_acct_id = self.cursor.execute("SELECT account_id FROM sso WHERE username = (?)", (username,)).fetchone()[0]
        self.cursor.execute("INSERT INTO data VALUES (?, ?, ?, ?)", (saved_acct_id, account_number, self.routing_number, 0,))

        # Save
        self.con.commit()

    # Create the new account
    def create_new_account(self):
        username = self.__create_username()
        password = self.__create_password()
        email = self.__create_email()
        account_number = self.__generate_account_number()
        self.__add_to_database(username, password, email, account_number)

        return self.cursor.execute("SELECT account_id FROM sso WHERE username = (?)", (username,)).fetchone()[0]
