import socket

HOST = "127.0.0.1"
PORT = 5001


# -------------------------------------------------------
# Vigenere Decryption
# -------------------------------------------------------
def decrypt(ciphertext, key):

    result = ""
    key = key.upper()
    key_index = 0

    for ch in ciphertext:

        # Decrypt only alphabetic characters
        if ch.isalpha():

            # Convert ciphertext letter to number
            # A = 0, B = 1, ..., Z = 25
            c = ord(ch.upper()) - ord('A')

            # Convert key letter to number
            k = ord(key[key_index % len(key)]) - ord('A')

            # Vigenere decryption formula
            p = (c - k) % 26

            # Convert number back to letter
            decrypted = chr(p + ord('A'))

            # Preserve lowercase letters
            if ch.islower():
                decrypted = decrypted.lower()

            result += decrypted

            # Move to next key character
            key_index += 1

        else:
            # Keep spaces, numbers and special characters unchanged
            result += ch

    return result


# -------------------------------------------------------
# Server
# -------------------------------------------------------

# Create TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow the port to be reused after stopping the server
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind server to IP and port
server.bind((HOST, PORT))

# Listen for client connection
server.listen(1)

print("Waiting for client...")

# Accept connection
conn, address = server.accept()

print("Connected to:", address)

# Receive ONLY ciphertext
ciphertext = conn.recv(4096).decode()

print("Received Ciphertext:", ciphertext)

# Server enters the secret key separately
key = input("Enter secret key: ")

# Decrypt the ciphertext
plaintext = decrypt(ciphertext, key)

print("Decrypted Plaintext:", plaintext)

# Close connection
conn.close()
server.close()