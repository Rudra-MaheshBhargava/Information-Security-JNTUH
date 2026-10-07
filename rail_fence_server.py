import socket

HOST = "127.0.0.1"
PORT = 5001


# -------------------------------------------------------
# Rail Fence Decryption
# -------------------------------------------------------
def decrypt(ciphertext, rails):

    if rails <= 1:
        return ciphertext

    length = len(ciphertext)

    # Create an empty fence
    fence = [['' for _ in range(length)] for _ in range(rails)]

    row = 0
    direction = 1

    # Mark the positions that belong to the zig-zag pattern
    for column in range(length):

        fence[row][column] = '*'

        # Change direction at top and bottom
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1

        row += direction

    # Fill the marked positions with ciphertext
    index = 0

    for i in range(rails):
        for j in range(length):

            if fence[i][j] == '*' and index < length:
                fence[i][j] = ciphertext[index]
                index += 1

    # Read the characters following the zig-zag pattern
    result = ""

    row = 0
    direction = 1

    for column in range(length):

        result += fence[row][column]

        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1

        row += direction

    return result


# -------------------------------------------------------
# Server
# -------------------------------------------------------

# Create TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow the port to be reused
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind server to IP and port
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
# In Rail Fence, the key is the number of rails
rails = int(input("Enter number of rails: "))

# Decrypt ciphertext
plaintext = decrypt(ciphertext, rails)

print("Decrypted Plaintext:", plaintext)

# Close connection
conn.close()
server.close()