import socket


# ---------------------------------------------------------
# Convert key word into a 3x3 matrix
# ---------------------------------------------------------

def create_key_matrix(key):
    # Convert key to uppercase and keep only alphabetic characters
    key = ''.join(ch for ch in key.upper() if ch.isalpha())

    # For a 3x3 matrix, only the first 9 letters are required.
    # If the key is longer than 9 letters, extra letters are ignored.
    key = key[:9]

    # Convert each letter into its numerical value
    # A = 0, B = 1, C = 2, ..., Z = 25
    numbers = [ord(ch) - ord('A') for ch in key]

    # Create the 3x3 key matrix
    matrix = [
        numbers[0:3],
        numbers[3:6],
        numbers[6:9]
    ]

    return matrix


# ---------------------------------------------------------
# Find modular inverse
# ---------------------------------------------------------
def mod_inverse(a, m):

    for i in range(1, m):

        if (a * i) % m == 1:
            return i

    return None


# ---------------------------------------------------------
# Calculate determinant of 3x3 matrix
# ---------------------------------------------------------
def determinant(matrix):

    a = matrix[0][0]
    b = matrix[0][1]
    c = matrix[0][2]

    d = matrix[1][0]
    e = matrix[1][1]
    f = matrix[1][2]

    g = matrix[2][0]
    h = matrix[2][1]
    i = matrix[2][2]

    det = (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    )

    return det


# ---------------------------------------------------------
# Calculate inverse of 3x3 key matrix
# ---------------------------------------------------------
def inverse_matrix(key):

    # Calculate determinant
    det = determinant(key)

    # Hill Cipher works modulo 26
    det = det % 26

    # Find inverse of determinant modulo 26
    det_inverse = mod_inverse(det, 26)

    # If determinant has no inverse,
    # the key cannot be used.
    if det_inverse is None:
        return None


    # -----------------------------------------------------
    # Calculate cofactor matrix
    # -----------------------------------------------------

    a = key[0][0]
    b = key[0][1]
    c = key[0][2]

    d = key[1][0]
    e = key[1][1]
    f = key[1][2]

    g = key[2][0]
    h = key[2][1]
    i = key[2][2]

    cofactor = [

        [
            (e * i - f * h),
            -(d * i - f * g),
            (d * h - e * g)
        ],

        [
            -(b * i - c * h),
            (a * i - c * g),
            -(a * h - b * g)
        ],

        [
            (b * f - c * e),
            -(a * f - c * d),
            (a * e - b * d)
        ]
    ]


    # -----------------------------------------------------
    # Transpose cofactor matrix
    # -----------------------------------------------------

    adjoint = [
        [cofactor[j][i] for j in range(3)]
        for i in range(3)
    ]


    # -----------------------------------------------------
    # Calculate inverse matrix
    #
    # K^-1 = det^-1 × adjoint(K) mod 26
    # -----------------------------------------------------

    inverse = [

        [
            (adjoint[i][j] * det_inverse) % 26
            for j in range(3)
        ]

        for i in range(3)
    ]

    return inverse


# ---------------------------------------------------------
# Hill Cipher Decryption
# ---------------------------------------------------------
def hill_decrypt(ciphertext, key):

    # Find inverse of key matrix
    inverse = inverse_matrix(key)

    if inverse is None:
        return None

    result = ""

    # Process ciphertext 3 letters at a time
    for i in range(0, len(ciphertext), 3):

        # Convert ciphertext letters to numbers
        x1 = ord(ciphertext[i]) - ord('A')
        x2 = ord(ciphertext[i + 1]) - ord('A')
        x3 = ord(ciphertext[i + 2]) - ord('A')


        # -------------------------------------------------
        # P = K^-1 × C mod 26
        # -------------------------------------------------

        y1 = (
            inverse[0][0] * x1 +
            inverse[0][1] * x2 +
            inverse[0][2] * x3
        ) % 26

        y2 = (
            inverse[1][0] * x1 +
            inverse[1][1] * x2 +
            inverse[1][2] * x3
        ) % 26

        y3 = (
            inverse[2][0] * x1 +
            inverse[2][1] * x2 +
            inverse[2][2] * x3
        ) % 26


        # Convert numbers back to letters
        result += chr(y1 + ord('A'))
        result += chr(y2 + ord('A'))
        result += chr(y3 + ord('A'))

    return result


# ---------------------------------------------------------
# SOCKET SERVER
# ---------------------------------------------------------

server = socket.socket()

# Bind server to localhost and port 5001
server.bind(("127.0.0.1", 5001))

# Listen for client
server.listen(1)

print("Waiting for client...")


# Accept client connection
conn, addr = server.accept()

print("Connected to:", addr)


# ---------------------------------------------------------
# Receive ONLY ciphertext
# ---------------------------------------------------------

ciphertext = conn.recv(1024).decode()

print("Received ciphertext:", ciphertext)


# ---------------------------------------------------------
# Server enters the SECRET KEY
# ---------------------------------------------------------

key_word = input("Enter 9-letter secret key: ")


# Convert word into 3x3 matrix
key = create_key_matrix(key_word)


if key is None:

    print("Invalid key!")
    print("Key must contain exactly 9 letters.")

else:

    # Display key matrix
    print("\nKey Matrix:")

    for row in key:
        print(row)


    # -----------------------------------------------------
    # Decrypt ciphertext
    # -----------------------------------------------------

    plaintext = hill_decrypt(ciphertext, key)


    if plaintext is None:

        print("\nInvalid key matrix!")

        print(
            "The determinant of the key matrix "
            "must have an inverse modulo 26."
        )

    else:

        print("\nDecrypted plaintext:", plaintext)


# Close connection
conn.close()
server.close()