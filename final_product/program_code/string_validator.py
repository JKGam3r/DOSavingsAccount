# Contains a list of functions dealing with validating usernames, passwords, and emails

import hashlib # Used for key hashing
import os # Used for generating a random bit of salt for each password

# Allowed special characters for passwords
special_characters = ['@', '#','!','~','$','%','^',
                '&','*','(',',','-','+',
                ':','.',',','<','>','?','|']

# Characters not allowed for passwords
forbidden_characters = [
    ' ',
    '/',
    '\\',
    '\'',
    '"'
]

# Creates a random bit of text (salt) and hash key
# This method simply calls functions from other modules, so it is not tested in this project
# Source of help: # https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
def generate_password_hash(original):
    salt = os.urandom(32)  # Remember this

    key =  hashlib.pbkdf2_hmac(
        'sha256',  # The hash digest algorithm for HMAC
        original.encode('utf-8'),  # Convert the password to bytes
        salt,  # Provide the salt
        100000  # It is recommended to use at least 100,000 iterations of SHA-256
    )

    return (salt, key)

# Compares the hashed password in the database to the inputted password
# This method simply calls functions from other modules, so it is not tested in this project
# Source of help: # https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
def compare_passwords(input_password, database_password):
    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        input_password.encode('utf-8'),  # Convert the password to bytes
        database_password[:32], # The salt
        100000
    )

    # The key generated above should be the same as the one originally created (stored in the database)
    return new_key == database_password[32:]

# Given a string, checks to see if the password meets the minimum length
def is_minimum_length(password, min_length):
    return len(password) >= min_length

# Given a string, checks to see if the password has a minimum number of special characters
def is_min_num_special_chars(password, min_special_chars):
    char_count = 0

    for c in password:
        if c in special_characters:
            char_count += 1

    return char_count >= min_special_chars

# Given a string, checks to see if the password contains the minimum number of lower case letters
def is_min_num_lower_case(password, min_low_case):
    char_count = 0

    for c in password:
        if c >= 'a' and c <= 'z':
            char_count += 1

    return char_count >= min_low_case

# Given a string, checks to see if the password contains the minimum number of upper case letters
def is_min_num_upper_case(password, min_capitals):
    char_count = 0

    for c in password:
        if c >= 'A' and c <= 'Z':
            char_count += 1

    return char_count >= min_capitals

# Given a string, checks to see if the password contains the minimum number of numbers
def is_min_num_digits(password, min_nums):
    char_count = 0

    for c in password:
        if c >= '0' and c <= '9':
            char_count += 1

    return char_count >= min_nums

# Checks to see if a string has characters not allowed for a username or password
def has_forbidden_chars(s):
    for c in s:
        if c in forbidden_characters:
            print(f"Error: Character '{c}' is not allowed.")
            return True

    return False

# Given a string, checks to see if the password is valid
def is_valid_password(password, min_length=12, min_special_chars=0, min_low_case=0, min_capitals=0, min_nums=0):
    if not is_minimum_length(password, min_length):
        print(f"Password must be a minimum of {min_length} characters.")
        return False
    if not is_min_num_special_chars(password, min_special_chars):
        print(f"Please use at least {min_special_chars} special character(s).")
        return False
    if not is_min_num_lower_case(password, min_low_case):
        print(f"Please use at least {min_low_case} lower case letter(s).")
        return False
    if not is_min_num_upper_case(password, min_capitals):
        print(f"Please use at least {min_capitals} upper case letter(s).")
        return False
    if not is_min_num_digits(password, min_nums):
        print(f"Please use at least {min_nums} number(s).")
        return False
    if has_forbidden_chars(password):
        print(f"Entry contains forbidden characters.")
        return False

    return True

# Checks to see if the symbols for an email are present, in the CORRECT order ('@', followed by '.')
def contains_email_symbols(email_address):
    num_at_symbols = 0
    num_dot_symbols = 0

    for c in email_address:
        if c == '@':
            if num_dot_symbols > 0: # Dot found before at symbol
                return False
            num_at_symbols += 1
        elif c == '.':
            num_dot_symbols += 1

    return num_at_symbols == 1 and num_dot_symbols == 1

# Checks to see if the general format of an email is met
def is_valid_email(email_address):
    if has_forbidden_chars(email_address) or not contains_email_symbols(email_address):
        return False

    temp = email_address.split('@')
    s = temp[1].split('.')
    s.append(temp[0])

    return len(s[0]) > 0 and len(s[1]) > 0 and len(s[2]) > 0

# Checks to see if a string consists of only numbers
def is_all_numbers(s):
    num_of_decimals = 0

    for c in s:
        if c < '0' or c > '9':
            if c == '.': # 1 decimal allowed
                num_of_decimals += 1
            else: # all other characters
                return False

    # Only a decimal - not allowed
    if len(s) <= 1 and num_of_decimals >= 1:
        return False

    return num_of_decimals <= 1

'''
    Hides the name of an email address using asterisks
        num_chars = number of characters in the username
        if num_chars <= 2, hide all of the characters
        else, hide all of the characters besides the first and last ones
'''
def hidden_email_address(email):
    # Don't bother modifying the string if it isn't a valid email address to begin with
    if not is_valid_email(email):
        return email

    # Find the '@' symbol
    parts = email.split('@')
    name_chars = parts[0]
    domain_chars = parts[1]
    new_name = ""

    # Convert appropriate characters to '*'
    nc_len = len(name_chars)
    if nc_len <= 2: # Convert all username characters to asterisks
        new_name = '*' * nc_len
    else: # Only convert the middle characters to asterisks
        new_name = name_chars[0] + ('*' * (nc_len - 2)) + name_chars[nc_len - 1]

    # Return the converted string
    return new_name + '@' + domain_chars