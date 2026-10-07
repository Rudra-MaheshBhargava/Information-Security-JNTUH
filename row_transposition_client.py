import socket

HOST = "127.0.0.1"
PORT = 5001


# -------------------------------------------------------
# Row Transposition Encryption
# -------------------------------------------------------
def encrypt(plaintext, key):

    # Remove spaces from plaintext
    # because they are not considered during transposition
    plaintext = ''.join(ch for ch in plaintext if not ch.isspace())

    # Number of columns is decided by the key
    columns = len(key)

    # Calculate number of rows required
    rows = (len(plaintext) + columns - 1) // columns

    # Add X to fill the last row if required
    while len(plaintext) < rows * columns:
        plaintext += 'X'

    # Create the matrix row by row
    matrix = []

    index = 0

    for i in range(rows):
        row = []

        for j in range(columns):
            row.append(plaintext[index])
            index += 1

        matrix.append(row)

    # Read columns according to the sorted key
    ciphertext = ""

    # Sort key characters with their original positions
    order = sorted(range(columns), key=lambda x: key[x])

    for column in order:

        for row in range(rows):
            ciphertext += matrix[row][column]

    return ciphertext


# -------------------------------------------------------
# Client
# -------------------------------------------------------

plaintext = input("Enter plaintext: ")
key = input("Enter key: ")

# Encrypt plaintext locally
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