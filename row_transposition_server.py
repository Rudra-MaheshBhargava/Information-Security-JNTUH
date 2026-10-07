import socket

HOST = "127.0.0.1"
PORT = 5001


# -------------------------------------------------------
# Row Transposition Decryption
# -------------------------------------------------------
def decrypt(ciphertext, key):

    columns = len(key)

    # Calculate number of rows
    rows = len(ciphertext) // columns

    # Create an empty matrix
    matrix = [['' for _ in range(columns)] for _ in range(rows)]

    # Determine the order in which columns were read
    order = sorted(range(columns), key=lambda x: key[x])

    index = 0

    # Fill the matrix column by column
    for column in order:

        for row in range(rows):
            matrix[row][column] = ciphertext[index]
            index += 1

    # Read the matrix row by row
    plaintext = ""

    for row in range(rows):
        for column in range(columns):
            plaintext += matrix[row][column]

    # Remove padding X characters
    plaintext = plaintext.rstrip('X')

    return plaintext


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

# Decrypt ciphertext
plaintext = decrypt(ciphertext, key)

print("Decrypted Plaintext:", plaintext)

# Close connection
conn.close()
server.close()