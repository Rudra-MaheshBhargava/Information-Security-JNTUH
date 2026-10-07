import socket

HOST = "127.0.0.1"
PORT = 5001


# -------------------------------------------------------
# One-Time Pad Decryption
# -------------------------------------------------------
def decrypt(ciphertext, key):

    result = ""
    key_index = 0

    for ch in ciphertext:

        # Decrypt only alphabetic characters
        if ch.isalpha():

            # Convert ciphertext letter to number
            # A = 0, B = 1, ..., Z = 25
            c = ord(ch.upper()) - ord('A')

            # Get corresponding key letter
            k = ord(key[key_index].upper()) - ord('A')

            # OTP decryption formula
            p = (c - k) % 26

            # Convert number back to letter
            decrypted = chr(p + ord('A'))

            # Preserve lowercase letters
            if ch.islower():
                decrypted = decrypted.lower()

            result += decrypted

            key_index += 1

        else:
            # Keep spaces and special characters unchanged
            result += ch

    return result


# -------------------------------------------------------
# Server
# -------------------------------------------------------

# Create TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow port to be reused
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind server
server.bind((HOST, PORT))

# Listen for client
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

# Remove non-alphabetic characters from key
key = ''.join(ch for ch in key if ch.isalpha())

# Check that the key is long enough
required_length = sum(ch.isalpha() for ch in ciphertext)

if len(key) < required_length:
    print("Key is too short.")
else:
    # Decrypt ciphertext
    plaintext = decrypt(ciphertext, key)

    print("Decrypted Plaintext:", plaintext)

# Close connection
conn.close()
server.close()