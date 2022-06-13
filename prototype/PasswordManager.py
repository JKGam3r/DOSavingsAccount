import hashlib # For key hashing
import os # Random generation of salt

# Hashing
# https://nitratine.net/blog/post/how-to-hash-passwords-in-python/

# Create a random bit of text (salt) and hash key
def generatePasswordHash(original):
    salt = os.urandom(32)  # Remember this

    key =  hashlib.pbkdf2_hmac(
        'sha256',  # The hash digest algorithm for HMAC
        original.encode('utf-8'),  # Convert the password to bytes
        salt,  # Provide the salt
        100000  # It is recommended to use at least 100,000 iterations of SHA-256
    )

    return (salt, key)

# Compare the hashed password in the database to the inputted password
def comparePasswords(inputPassword, databasePassword):
    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        inputPassword.encode('utf-8'),  # Convert the password to bytes
        databasePassword[:32], # The salt
        100000
    )

    # The key generated above should be the same as the one originally created (stored in the database)
    return new_key == databasePassword[32:]