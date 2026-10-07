import socket


def create_matrix(key):
    key = key.upper().replace("J", "I")

    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    chars = ""

    for ch in key + alphabet:
        if ch.isalpha() and ch not in chars:
            chars += ch

    matrix = [chars[i:i + 5] for i in range(0, 25, 5)]

    return matrix


def find_position(matrix, ch):
    for i in range(5):
        for j in range(5):
            if matrix[i][j] == ch:
                return i, j


def playfair_decrypt(ciphertext, key):

    matrix = create_matrix(key)

    result = ""

    for i in range(0, len(ciphertext), 2):

        a = ciphertext[i]
        b = ciphertext[i + 1]

        r1, c1 = find_position(matrix, a)
        r2, c2 = find_position(matrix, b)

        # Same row
        if r1 == r2:

            result += matrix[r1][(c1 - 1) % 5]
            result += matrix[r2][(c2 - 1) % 5]

        # Same column
        elif c1 == c2:

            result += matrix[(r1 - 1) % 5][c1]
            result += matrix[(r2 - 1) % 5][c2]

        # Rectangle
        else:

            result += matrix[r1][c2]
            result += matrix[r2][c1]

    return result


# Socket
server = socket.socket()

server.bind(("127.0.0.1", 5001))

server.listen(1)

print("Waiting for client...")

conn, addr = server.accept()

print("Connected to:", addr)

# Receive ONLY ciphertext
ciphertext = conn.recv(1024).decode() # Receive the ciphertext sent by the client and decode it from bytes to a string

print("Received ciphertext:", ciphertext)

# Server enters secret key
key = input("Enter secret key: ")

plaintext = playfair_decrypt(ciphertext, key) # Decrypt the received ciphertext using the provided key

print("Decrypted plaintext:", plaintext)

conn.close()
server.close()