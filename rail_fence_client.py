import socket

HOST = "127.0.0.1"
PORT = 5001


# -------------------------------------------------------
# Rail Fence Encryption
# -------------------------------------------------------
def encrypt(plaintext, rails):

    # If only one rail is used, no encryption is required
    if rails <= 1:
        return plaintext

    result = ""

    # Create a list for each rail
    fence = ['' for _ in range(rails)]

    row = 0
    direction = 1

    # Place each character in a zig-zag pattern
    for ch in plaintext:

        fence[row] += ch

        # Change direction at the top and bottom rail
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1

        row += direction

    # Read the characters row by row
    for rail in fence:
        result += rail

    return result


# -------------------------------------------------------
# Client
# -------------------------------------------------------

plaintext = input("Enter plaintext: ")
rails = int(input("Enter number of rails: "))

# Encrypt plaintext locally
ciphertext = encrypt(plaintext, rails)

print("Ciphertext:", ciphertext)

# Create TCP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
client.connect((HOST, PORT))

# Send ONLY ciphertext
# The number of rails is NOT sent through the socket
client.send(ciphertext.encode())

client.close() 