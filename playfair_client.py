import socket


def create_matrix(key): 
    key = key.upper().replace("J", "I")

    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    chars = ""

    for ch in key + alphabet: # Loop through the key and alphabet to create a string of unique characters
        if ch.isalpha() and ch not in chars: # Check if character is alphabetic and not already in the unique characters string
            chars += ch

    matrix = [chars[i:i + 5] for i in range(0, 25, 5)] # Create a 5x5 matrix from the unique characters

    return matrix


def find_position(matrix, ch): # Find the position of a character in the matrix
    for i in range(5):
        for j in range(5):
            if matrix[i][j] == ch:
                return i, j


def prepare_text(text):
    text = text.upper().replace("J", "I")
    text = ''.join(ch for ch in text if ch.isalpha()) # Remove non-alphabetic characters from the text 

    result = "" # Initialize the result string
    i = 0 # Initialize the index for iterating through the text

    while i < len(text): # Loop through the text to prepare it for encryption

        a = text[i] # Get the current character

        if i + 1 < len(text): # Check if there is a next character in the text
            b = text[i + 1] # Get the next character
        else:
            b = "X" # If there is no next character, set b to "X" 

        if a == b:
            result += a + "X" # If the current character is the same as the next character, add "X" after the current character and move to the next character
            i += 1
        else:
            result += a + b # If the current character is different from the next character, add both characters to the result and move to the next pair of characters
            i += 2

    if len(result) % 2 != 0: # If the length of the result is odd, add "X" to the end of the result to make it even
        result += "X"

    return result


def playfair_encrypt(text, key):

    matrix = create_matrix(key) # Create the 5x5 matrix using the provided key
    text = prepare_text(text) # Prepare the text for encryption by removing non-alphabetic characters, replacing 'J' with 'I', and ensuring that the text has an even length

    result = "" # Initialize the result string for the encrypted text

    for i in range(0, len(text), 2): # Loop through the prepared text in pairs of characters (two at a time)

        a = text[i] # Get the current character in the pair
        b = text[i + 1] # Get the next character in the pair

        r1, c1 = find_position(matrix, a) # Find the row and column of the first character in the matrix
        r2, c2 = find_position(matrix, b) # Find the row and column of the second character in the matrix

        # Same row
        if r1 == r2:

            result += matrix[r1][(c1 + 1) % 5] # Add the character to the right of the first character in the same row to the result (wrap around if necessary)
            result += matrix[r2][(c2 + 1) % 5] # Add the character to the right of the second character in the same row to the result (wrap around if necessary)

        # Same column
        elif c1 == c2:

            result += matrix[(r1 + 1) % 5][c1] # Add the character below the first character in the same column to the result (wrap around if necessary)
            result += matrix[(r2 + 1) % 5][c2] # Add the character below the second character in the same column to the result (wrap around if necessary)

        # Rectangle
        else:

            result += matrix[r1][c2] # Add the character in the same row as the first character and the same column as the second character to the result
            result += matrix[r2][c1] # Add the character in the same row as the second character and the same column as the first character to the result

    return result


# Socket
client = socket.socket()

client.connect(("127.0.0.1", 5001))

plaintext = input("Enter plaintext: ")
key = input("Enter encryption key: ")

ciphertext = playfair_encrypt(plaintext, key)

print("Encrypted text:", ciphertext)

# Send ONLY ciphertext
client.send(ciphertext.encode())

client.close()