import socket

def caesar_decrypt(ciphertext, key):
    result = ""

    for ch in ciphertext:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result += chr((ord(ch) - base - key) % 26 + base)
        else:
            result += ch

    return result


server = socket.socket()
server.bind(("127.0.0.1", 5001))
server.listen(1)

print("Waiting for client...")

conn, addr = server.accept()

ciphertext = conn.recv(1024).decode()

print("Received ciphertext:", ciphertext)

key = int(input("Enter secret key: "))

plaintext = caesar_decrypt(ciphertext, key)

print("Decrypted plaintext:", plaintext)

conn.close()
server.close()