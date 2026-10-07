import socket

HOST = "127.0.0.1"
PORT = 5001


# -------------------------------------------------------
# Vigenere Encryption
# Polyalphabetic Cipher uses a repeating key.
# Example:
# Plaintext :  HELLO
# Key       :  KEYKE
# -------------------------------------------------------
def encrypt(plaintext, key):

    result = ""
    key = key.upper()
    key_index = 0

    for ch in plaintext:

        # Encrypt only alphabetic characters
        if ch.isalpha():

            # Convert plaintext letter to number
            # A = 0, B = 1, ..., Z = 25
            p = ord(ch.upper()) - ord('A')

            # Convert key letter to number
            k = ord(key[key_index % len(key)]) - ord('A')

            # Vigenere encryption formula
            c = (p + k) % 26

            # Convert number back to letter
            encrypted = chr(c + ord('A'))

            # Preserve lowercase letters
            if ch.islower():
                encrypted = encrypted.lower()

            result += encrypted

            # Move to next key character
            key_index += 1

        else:
            # Keep spaces, numbers and special characters unchanged
            result += ch

    return result


# -------------------------------------------------------
# Client
# -------------------------------------------------------

plaintext = input("Enter plaintext: ")
key = input("Enter key: ")

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