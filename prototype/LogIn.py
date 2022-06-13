import pwinput # Used for passwords
import sqlite3 # Database

from PasswordManager import comparePasswords

# Deals with everything needed to sign in; notice how there are no other variables in the constructor besides
# # the cursor, con, and routing number (to help prevent from outside access)
class SignIn:
    # Constructor
    def __init__(self, cursor):
        # Create cursor for manipulating the table
        self.cursor = cursor

    # Single sign-on (SSO) authentication
    def __prompt(self):
        username = input("Username: ")
        password = pwinput.pwinput("Password: ")

        return username, password

    # Prevent SQL injection and other harmful character/ string combinations by breaking up into a tuple (instead of concatenation)
    # * Parameterized query; tries to find a password
    def __search(self, username):
        hashedPassword = None

        pass_obj = self.cursor.execute("SELECT password FROM sso WHERE username = (?)", (username,)).fetchone()
        if pass_obj is not None:
            hashedPassword = pass_obj[0]

        return hashedPassword

    # The input username and password is associated with an entry in the table
    def __isValid(self, password, hashed_password):
        if hashed_password is not None:
            return comparePasswords(password, hashed_password)
        else:  # No such entry
            return False

    # Wraps all methods in one to ask the user to sign into their account
    def requestSignIn(self):
        username, password = self.__prompt()
        hashed_password = self.__search(username)
        is_valid_credentials = self.__isValid(password, hashed_password)
        cred_id = -1

        if is_valid_credentials:
            cred_id = self.cursor.execute("SELECT account_id FROM sso WHERE username = (?)", (username,)).fetchone()[0]

        return cred_id