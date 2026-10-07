import socket

def caesar_encrypt(text, key):
    result = ""

    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result += chr((ord(ch) - base + key) % 26 + base)
        else:
            result += ch

    return result


client = socket.socket()
client.connect(("127.0.0.1", 5001))

plaintext = input("Enter plaintext: ")
key = int(input("Enter encryption key: "))

ciphertext = caesar_encrypt(plaintext, key)

print("Encrypted text:", ciphertext)

client.send(ciphertext.encode())

client.close()