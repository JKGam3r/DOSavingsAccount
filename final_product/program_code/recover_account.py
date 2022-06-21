# Responsible for recovering a user's account

import pwinput # Used for hiding passwords

from SavingsDatabaseApplication.program_code.string_validator import * # Used for hashing and verifying password validity (meets requirements)
from SavingsDatabaseApplication.program_code.create_account import * # Used for hashing and verifying password validity (meets requirements)

# Manages all methods dealing with recovering a user's account
class AccountRecover:
    # Constructor
    def __init__(self, cursor, connection, cred_table, alerts_table, min_special_chars, min_capitals, min_nums):
        # Database variables
        self.cursor = cursor
        self.connection = connection

        # The credentials table with usernames, passwords, and email addresses
        self.cred_table = cred_table

        # The alerts table with notifications
        self.alerts_table = alerts_table

        # Cancels the request
        self.cancel_recovery_request = False

        # Password requirements
        self.min_special_chars = min_special_chars
        self.min_capitals = min_capitals
        self.min_nums = min_nums

    # Asks the user for either a username or email for account recovery
    def ask_for_cred(self):
        # The username associated with this account
        username = ""

        # The email address to send a verification code to
        email = ""

        # Initial messages
        print("You can recover your account by referring to your username or email.")
        print("Please note that you can cancel this request for an account recovery by typing 'Cancel' (no quotes) and entering.")

        # Keep iterating while the response is invalid
        valid_response = False
        while not valid_response:
            # Display options
            print("Type 1 and Enter to recover your account by username.")
            print("Type 2 and Enter to recover your account by email.")
            response = input("Your response: ").upper()

            if response == 'CANCEL': # stop the request
                self.cancel_recovery_request = True
                valid_response = True
                return username, email
            elif response == '1': # user inputted username
                valid_response = True

                # Requests the user's username
                typed_username = input("Please enter your username: ")

                if typed_username.upper() == 'CANCEL':  # stop the request
                    self.cancel_recovery_request = True
                    return username, email

                # Used to (1) verify that this is a valid account and (2) get the email address
                retrieved_email = self.cursor.execute(f"SELECT email FROM {self.cred_table} WHERE username = (?)",
                                                      (typed_username,)).fetchone()

                if retrieved_email is not None: # there is a valid account with an email address (email = "" if not set)
                    if retrieved_email[0] != "": # Email address set
                        username = typed_username
                        email = retrieved_email[0]
                    else: # There is no email address associated with this account
                        print("No email address was set for this account.")
                else:
                    print("No account found under this username.")

            elif response == '2': # user inputted email
                valid_response = True

                # Requests the user's username
                typed_email = input("Please enter your email: ")

                if typed_email.upper() == 'CANCEL':  # stop the request
                    self.cancel_recovery_request = True
                    return username, email

                # Used to (1) verify that this is a valid account and (2) get the username
                emails_username = self.cursor.execute(f"SELECT username FROM {self.cred_table} WHERE email = (?)",
                                                  (typed_email,)).fetchone()
                if emails_username is not None:
                    print(f"An email will be sent to the given address with the username '{emails_username}.'")
                    username = emails_username
                    email = typed_email
                else:
                    print("Email not associated with any account.")
            else: # invalid response; try again
                print("Invalid response.")

        print()

        return username, email

    # Calls all related methods to try and recover the user's account
    def recover_account(self):
        # Get the username and email
        username, email = self.ask_for_cred()

        # If true, the user typed 'Cancel' to stop the request, or no valid email address was found
        if self.cancel_recovery_request or email == "":
            return

        recover_creator = AccountCreator(None, None, None, None, None, None, None, None, None)
        code = recover_creator.send_email(username, email)

        # Keep iterating until a valid response is received
        valid_response = False
        while not valid_response:

            # The code that is typed by the user (for confirming that this is indeed the user's account)
            input_code = input("Input the code you received (only input numbers): ")

            other_actions = input_code.upper()
            # User wants to cancel the request for a password reset
            if other_actions == 'CANCEL':
                print("Request cancelled.")
                valid_response = True
                return
            elif other_actions == 'RESEND': # Send a new code
                code = recover_creator.send_email(username, email)
            else:
                # Make sure code consists of only digits and is the right length
                if len(input_code) == 6 and is_min_num_digits(input_code, 6):
                    if int(input_code) == code: # Input and email codes are the same
                        different_passwords = True

                        # Keep iterating until either password change is successful or user cancels the request
                        while different_passwords:

                            # Reset cancelled
                            new_password1 = pwinput.pwinput("Enter your new password: ")
                            if new_password1.upper() == 'CANCEL':
                                print("Pasword reset cancelled.")
                                valid_response = True
                                return

                            # Reset cancelled
                            new_password2 = pwinput.pwinput("Please retype your new password: ")
                            if new_password2.upper() == 'CANCEL':
                                print("Pasword reset cancelled.")
                                valid_response = True
                                return

                            # Passwords match
                            if new_password1 == new_password2:
                                # All necessary (types of) characters are included in the new password
                                if is_valid_password(new_password1, min_special_chars=self.min_special_chars, min_capitals=self.min_capitals, min_nums=self.min_nums):
                                    different_passwords = False
                                    salt_and_key = generate_password_hash(new_password1)
                                    storage = salt_and_key[0] + salt_and_key[1]
                                    self.cursor.execute(f"UPDATE {self.cred_table} SET password = ? WHERE email = ?",
                                                        (storage, email,))  # CHECK THIS PART
                                    self.connection.commit()

                                    account_ID = self.cursor.execute

                                    print("New password successfully saved.  Please log back in.")
                                    valid_response = True

                                    # Add a new alert
                                    all_alerts = \
                                    cursor.execute(f"SELECT alerts FROM {self.alerts_table} WHERE account_id = (?)",
                                                   (account_ID,)).fetchone()[0]
                                    new_string = f"{format_date()} - Your password was changed to recover your account.\n{all_alerts}"
                                    cursor.execute(f"UPDATE {self.alerts_table} SET alerts = ? WHERE account_id = ?",
                                                   (new_string, account_ID,))

                                    return
                            else:
                                print("Passwords do not match.")
                    else:
                        print("Incorrect passcode.")
                else:
                    print("Invalid code format and/ or length.")

        print()