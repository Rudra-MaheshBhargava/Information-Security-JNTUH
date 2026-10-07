import socket

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def monoalphabetic_decrypt(ciphertext, key):
    result = ""

    for ch in ciphertext:

        if ch.isalpha():

            index = key.index(ch.upper())

            decrypted = alphabet[index]

            if ch.islower():
                decrypted = decrypted.lower()

            result += decrypted

        else:
            result += ch

    return result


# Create socket
server = socket.socket()

# Bind server
server.bind(("127.0.0.1", 5001))

# Listen
server.listen(1)

print("Waiting for client...")

# Accept connection
conn, addr = server.accept()

print("Connected to:", addr)

# Receive ONLY ciphertext
ciphertext = conn.recv(1024).decode()

print("Received ciphertext:", ciphertext)

# Server enters secret key
key = input("Enter secret key: ").upper()

# Validate key
if len(key) != 26 or len(set(key)) != 26 or not key.isalpha():
    print("Invalid key!")
    print("Key must contain 26 unique letters.")
else:

    # Decrypt
    plaintext = monoalphabetic_decrypt(ciphertext, key)

    print("Decrypted plaintext:", plaintext)

# Close connection
conn.close()
server.close()