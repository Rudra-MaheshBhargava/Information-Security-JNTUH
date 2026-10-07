import socket

HOST = "127.0.0.1"
PORT = 5001


# -------------------------------------------------------
# One-Time Pad Encryption
# -------------------------------------------------------
def encrypt(plaintext, key):

    result = ""
    key_index = 0

    for ch in plaintext:

        # Encrypt only alphabetic characters
        if ch.isalpha():

            # Convert plaintext letter to number
            # A = 0, B = 1, ..., Z = 25
            p = ord(ch.upper()) - ord('A')

            # Get corresponding key letter
            k = ord(key[key_index].upper()) - ord('A')

            # OTP encryption formula
            c = (p + k) % 26

            # Convert number back to letter
            encrypted = chr(c + ord('A'))

            # Preserve lowercase letters
            if ch.islower():
                encrypted = encrypted.lower()

            result += encrypted

            key_index += 1

        else:
            # Keep spaces and special characters unchanged
            result += ch

    return result


# -------------------------------------------------------
# Client
# -------------------------------------------------------

plaintext = input("Enter plaintext: ")
key = input("Enter key: ")

# Remove non-alphabetic characters from the key
key = ''.join(ch for ch in key if ch.isalpha())

# OTP requires the key to be at least as long as
# the number of alphabetic characters in the plaintext.
# Extra key characters are simply not used.
required_length = sum(ch.isalpha() for ch in plaintext)

if len(key) < required_length:
    print("Key must be at least as long as the plaintext.")
    exit()

# Encrypt locally
ciphertext = encrypt(plaintext, key)

print("Ciphertext:", ciphertext)

# Create TCP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
client.connect((HOST, PORT))

# Send ONLY ciphertext
# The key is NOT sent through the socket
client.send(ciphertext.encode())

client.close()