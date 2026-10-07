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
# Hill Cipher Encryption
# ---------------------------------------------------------
def hill_encrypt(text, key):

    # Convert plaintext to uppercase
    # and remove spaces/special characters
    text = ''.join(ch for ch in text.upper() if ch.isalpha())

    # Hill Cipher with a 3x3 matrix works with
    # 3 letters at a time.
    # Add X as padding if required.
    while len(text) % 3 != 0:
        text += "X"

    result = ""

    # Process 3 letters at a time
    for i in range(0, len(text), 3):

        # Convert plaintext letters to numbers
        # A=0, B=1, ..., Z=25
        x1 = ord(text[i]) - ord('A')
        x2 = ord(text[i + 1]) - ord('A')
        x3 = ord(text[i + 2]) - ord('A')

        # Matrix multiplication:
        #
        # C = K × P mod 26

        y1 = (
            key[0][0] * x1 +
            key[0][1] * x2 +
            key[0][2] * x3
        ) % 26

        y2 = (
            key[1][0] * x1 +
            key[1][1] * x2 +
            key[1][2] * x3
        ) % 26

        y3 = (
            key[2][0] * x1 +
            key[2][1] * x2 +
            key[2][2] * x3
        ) % 26

        # Convert numbers back to letters
        result += chr(y1 + ord('A'))
        result += chr(y2 + ord('A'))
        result += chr(y3 + ord('A'))

    return result


# ---------------------------------------------------------
# SOCKET CLIENT
# ---------------------------------------------------------

client = socket.socket()

# Connect to server
client.connect(("127.0.0.1", 5001))


# ---------------------------------------------------------
# Get plaintext and key from client
# ---------------------------------------------------------

plaintext = input("Enter plaintext: ")

key_word = input("Enter 9-letter key: ")


# Convert key word into 3x3 matrix
key = create_key_matrix(key_word)


if key is None:

    print("Invalid key!")
    print("Key must contain exactly 9 letters.")

    client.close()
    exit()


# Display the generated key matrix
print("\nKey Matrix:")

for row in key:
    print(row)


# ---------------------------------------------------------
# Encrypt plaintext
# ---------------------------------------------------------

ciphertext = hill_encrypt(plaintext, key)

print("\nEncrypted text:", ciphertext)


# ---------------------------------------------------------
# Send ONLY ciphertext
# ---------------------------------------------------------
# The plaintext and key are NOT sent to the server.
client.send(ciphertext.encode())


# Close connection
client.close()