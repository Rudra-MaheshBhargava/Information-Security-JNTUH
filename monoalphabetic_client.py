import socket

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def monoalphabetic_encrypt(text, key):
    result = ""

    for ch in text:

        if ch.isalpha(): # Check if the character is an alphabet

            index = alphabet.index(ch.upper()) # Find the index of the character in the alphabet

            encrypted = key[index] # Get the corresponding character from the key

            if ch.islower(): # If the original character was lowercase, convert the encrypted character to lowercase
                encrypted = encrypted.lower()

            result += encrypted

        else:
            result += ch

    return result


# Create socket
client = socket.socket()

# Connect to server
client.connect(("127.0.0.1", 5001))

# Get plaintext
plaintext = input("Enter plaintext: ")

# Get encryption key
key = input("Enter 26-letter encryption key: ").upper() # Convert the key to uppercase

# Validate key
if len(key) != 26 or len(set(key)) != 26 or not key.isalpha(): # Check if the key is valid
    print("Invalid key!")
    print("Key must contain 26 unique letters.")
    client.close()
    exit()

# Encrypt
ciphertext = monoalphabetic_encrypt(plaintext, key)

print("Encrypted text:", ciphertext)

# Send ONLY ciphertext
client.send(ciphertext.encode())

# Close connection
client.close()