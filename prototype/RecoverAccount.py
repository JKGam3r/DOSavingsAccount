import smtplib # To send emails
import ssl # For encryption
import random # Random account number
import pwinput # For passwords
from email.mime.text import MIMEText # Makes the creation of the recovery email easy

from PasswordManager import *

# Manages all methods dealing with recovering a user's account
class AccountRecover:
    def __init__(self, cursor, con):
        self.cursor = cursor
        self.con = con

    # Asks the user for either a username or email for account recovery
    def __ask_for_cred(self):
        email = ""

        print("You can recover your account by referring to your username or email.")

        valid_response = False
        while not valid_response:
            print("Type 1 and Enter to recover your account by username")
            print("Type 2 and Enter to recover your account by email")
            response = input("Your response: ")

            if response == '1' or response == '2':
                valid_response = True
            else:
                print("Please type 1 or 2.")

            if response == '1': # username recovery
                typed_username = input("Please enter your username: ")
                retrieved_email = self.cursor.execute("SELECT email FROM sso WHERE username = (?)",
                                                  (typed_username,)).fetchone()
                if retrieved_email is not None:
                    print("Email found")
                    email = retrieved_email[0]
                else:
                    print("No account found under this username")

            elif response == '2':
                typed_email = input("Please enter your email: ")
                emails_username = self.cursor.execute("SELECT username FROM sso WHERE email = (?)",
                                                  (typed_email,)).fetchone()
                if typed_email is not None:
                    print("Email validated")
                    email = typed_email[0]
                else:
                    print("Email not associated with any account")

        return email

    # Generates a pseudo-random code
    def __generate_code(self):
        return random.randrange(100_000, 999_999)

    # Formats the code as a modified string version of the integer
    def __stringify_code(self, code):
        str_code = ""

        # Get each digit in the code
        while code > 0:
            digit = code % 10
            code = int(code / 10)

            str_code += (str(digit) + " ")

        # Will be in reverse order, rearrange
        return str_code[::-1]

    # Send an email
    def __send_email(self, email):
        if email == "":
            print("No email address found.")
            return

        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = input("Temporary - enter sender email: ") # temporary
        #sender_email = "my@gmail.com" # temporary
        receiver_email = email
        password = pwinput.pwinput("Temporary - enter sender password/ app code: ") # temporary
        #password = input("Type your password and press enter: ") # temporary
        code = self.__generate_code()
        stringified_code = self.__stringify_code(code)
        msg = MIMEText(f"Please type in the following 6-digit code into the banking program to continue.\nCode: {stringified_code}")

        msg['Subject'] = 'DO Recovery Code'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        return code

    # Calls all related methods to try and recover the user's account
    def recover_account(self):
        email = self.__ask_for_cred()
        code = self.__send_email(email)

        if email == "":
            return -1

        # The code inputted by the user
        input_code = input("Input the code you received (only input numbers): ")

        if int(input_code) == code:
            different_passwords = True

            while different_passwords:
                new_password1 = pwinput.pwinput("Enter your new password: ")
                new_password2 = pwinput.pwinput("Please retype your new password: ")

                if new_password1 == new_password2:
                    different_passwords = False
                    salt_and_key = generatePasswordHash(new_password1)
                    storage = salt_and_key[0] + salt_and_key[1]
                    self.cursor.execute("UPDATE sso SET password = ? WHERE email = ?",
                                   (storage, email,))  # CHECK THIS PART
                    self.con.commit()

                    account_ID = self.cursor.execute

                    print("New password successfully saved.")

                    # returns the account ID
                    return self.cursor.execute("SELECT account_id FROM sso WHERE email = (?)", (email,)).fetchone()[0]
        else:
            print("Incorrect passcode.")

        return -1 # account ID