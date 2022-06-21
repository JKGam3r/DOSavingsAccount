# This file is responsible for creating an account in the database

import datetime # Used for getting the time that the account was created
from email.mime.text import MIMEText # Used to piece together the recovery email
import platform # For getting the device name
import pwinput # Used for hiding passwords
import random # Used to generate a random account number
import smtplib # Used for sending emails
import ssl # Used for encryption

from SavingsDatabaseApplication.program_code.string_validator import * # Used for usernames, passwords, and emails
from SavingsDatabaseApplication.program_code.misc_functions import * # Used for formatting the date

# Manages the creation of a new account in the database
class AccountCreator:
    # Account number for the next new account - not a good way (at all) for generating an account number,
    # but is purely used for demonstration purposes (account number is not used very much)
    current_account_number = 10_000_000

    # Initialize "backbone" variables shared among main module and this one
    def __init__(self, cursor, connection, routing_number, cred_table, data_table, alerts_table, min_special_chars, min_capitals, min_nums):
        # Represents the database
        self.cursor = cursor
        self.connection = connection

        # The routing number associated with this "bank"
        self.routing_number = routing_number

        # The table with usernames, passwords, and emails
        self.cred_table = cred_table

        # The table with the users' data
        self.data_table = data_table

        # The table with alerts
        self.alerts_table = alerts_table

        # Cancels the creation of the account
        self.cancel_account_creation = False

        # Password requirements
        self.min_special_chars = min_special_chars
        self.min_capitals = min_capitals
        self.min_nums = min_nums

    # Prompts the user to enter a username
    def create_username(self):
        username = "" # Valid username to return
        valid_username = False # Change to true when user has entered a valid username

        print("You can cancel the creation of a new account at any point in this process by typing 'Cancel' (no quotes).")

        # Iterate while user has not cancelled and a valid username has not been entered
        while not valid_username:
            # Input username
            typed_username = input("Please enter in a username: ")

            # User cancelled account request
            if typed_username.lower() == 'cancel':
                print("Request cancelled.")
                self.cancel_account_creation = True
                return username

            if not has_forbidden_chars(typed_username):  # Make sure there are no forbidden characters
                # Tries to find a match in the database
                db_username = self.cursor.execute(f"SELECT account_id FROM {self.cred_table} WHERE username = (?)", (typed_username,)).fetchone()

                if db_username is None: # Typed username is not in the database
                    username = typed_username
                    valid_username = True
                else: # Username is already taken
                    print("Selected username is already taken.  Please try again.")

        print()
        return username

    # Prompts the user to enter a password
    def create_password(self):
        password = "" # Valid password to return
        same_passwords = False # Change to true when user has entered a valid password

        # Iterate while user has not cancelled and a valid password has not been entered
        while not same_passwords:
            password1 = pwinput.pwinput("Type in a password: ")
            if password1.lower() == 'cancel': # User cancelled account request
                print("Request cancelled.")
                self.cancel_account_creation = True
                return password

            password2 = pwinput.pwinput("Retype your password: ")
            if password2.lower() == 'cancel': # User cancelled account request
                print("Request cancelled.")
                self.cancel_account_creation = True
                return password

            if password1 == password2: # Same password typed both times
                if is_valid_password(password1, min_special_chars=self.min_special_chars, min_capitals=self.min_capitals, min_nums=self.min_nums): # Make sure password is valid
                    password = password1
                    same_passwords = True
            else: # Passwords are different
                print("Passwords do not match.  Please try again.")

        print()
        return password

    # Sends an email address and returns the code sent to that address
    def send_email(self, username, email):
        # There is no email address
        if email == "":
            return -1

        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = 'name@email.com' # Replace this line with a valid email address
        receiver_email = email
        password = 'password_here' # Replace this with a valid password (may have to use an app password)
        code = random.randrange(100_000, 999_999)
        modified_code = [int(x) for x in str(code)]
        msg_txt = f"This email is being sent to the account holder '{username}.'" \
                  f"\nPlease type in the following 6-digit code into the banking program to continue." \
                  f"\nCode: {code}" \
                  f"\n\nIf you were not expecting this email, please disregard it."
        msg = MIMEText(msg_txt)

        msg['Subject'] = 'DO Verification Code'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print(f"An email was sent to {hidden_email_address(email)}.  Please check your inbox for a code.")
        print()

        return code

    # Prompts the user for an email
    def create_email(self, username):
        email = "" # User's recovery email
        valid_response = False # User must choose Yes or No

        print("You have the option to set a recovery email.")
        print("* Please keep in mind that opting out will prevent account recovery.")

        while not valid_response:
            selection = input("Type Y for Yes, N for No: ").upper()

            if selection.lower() == 'cancel': # User cancelled account request
                print("Request cancelled.")
                self.cancel_account_creation = True
                return email

            if selection == "Y" or selection == "YES": # User wants to set a recovery email
                valid_response = True # Set boolean to true now
                valid_email = False # True if email address is acceptable

                # Keep iterating until a valid email address is found
                while not valid_email:
                    input_email = input("Please enter an email address: ")

                    if input_email.lower() == 'cancel':  # User cancelled account request
                        print("Request cancelled.")
                        self.cancel_account_creation = True
                        return email

                    if is_valid_email(input_email): # Acceptable email
                        valid_email = True

                        # Send a code to the user
                        code = self.send_email(username, input_email)

                        print("To resend a new code, type 'Resend' (no quotes).")

                        # Make sure email address is real and is the user's by sending a verification code
                        email_verified = False
                        while not email_verified:
                            # User's response
                            input_code = input("Input the code you received: ")

                            other_actions = input_code.upper()
                            # User cancelled the action
                            if other_actions == 'CANCEL':
                                print("Action cancelled.")
                                email_verified = True
                                return email
                            elif other_actions == 'RESEND': # User asked to resend the code
                                code = self.send_email(username, input_email)
                            else: # Should be the code
                                # Check if email address is real
                                if len(input_code) == 6 and is_min_num_digits(input_code, 6):
                                    if int(input_code) == code:  # Input and email codes are the same
                                        print("Email address verified.")
                                        email = input_email
                                        email_verified = True
                                    else:
                                        print("Incorrect code.")
                                else:
                                    print("Incorrect code length and/ or use of non-numbers found.")

                    else: # Email not accepted
                        print("Invalid email address.")

            elif selection == "N" or selection == "NO": # No recovery email requested
                print("You can set a recovery email at a later date.")
                valid_response = True
            else: # Invalid response
                print("Please type Y/N")

        print()

        return email

    # Generates a unique identifier for this user's account
    def generate_account_number(self):
        user_acct_number = AccountCreator.current_account_number
        AccountCreator.current_account_number += 1
        return str(user_acct_number)

    # Creates a new account (table entry) with all of the given arguments
    def add_to_database(self, username, password, email, account_number):
        # Make a hashed version of the password
        salt_and_key = generate_password_hash(password)
        storage = salt_and_key[0] + salt_and_key[1]

        # Put into the database
        self.cursor.execute(f"INSERT INTO {self.cred_table} VALUES (?, ?, ?, ?)", (None, username, storage, email,))
        acct_id = self.cursor.execute(f"SELECT account_id FROM {self.cred_table} WHERE username = (?)", (username,)).fetchone()[0]
        self.cursor.execute(f"INSERT INTO {self.data_table} VALUES (?, ?, ?, ?)", (acct_id, account_number, self.routing_number, 0,))
        self.cursor.execute(f"INSERT INTO {self.alerts_table} VALUES (?, ?)", (acct_id, f"{format_date()} - Account created.",))

        # Add a new alert informing the user they're signed in
        all_alerts = self.cursor.execute(f"SELECT alerts FROM {self.alerts_table} WHERE account_id = (?)", (acct_id,)).fetchone()[0]
        new_string = f"{format_date()} - Signed in on device {platform.node()}.\n{all_alerts}"
        self.cursor.execute(f"UPDATE {self.alerts_table} SET alerts = ? WHERE account_id = ?",
                       (new_string, acct_id,))

        # Save changes
        self.connection.commit()

    '''
    Creates a new account - this function is the only class method that
    needs to be called to add a new account/ entry to the table
    '''
    def create_new_account(self):
        username = self.create_username()
        if self.cancel_account_creation:
            return -1

        password = self.create_password()
        if self.cancel_account_creation:
            return -1

        email = self.create_email(username)
        if self.cancel_account_creation:
            return -1

        account_number = self.generate_account_number()
        self.add_to_database(username, password, email, account_number)

        return self.cursor.execute(f"SELECT account_id FROM {self.cred_table} WHERE username = (?)", (username,)).fetchone()[0]