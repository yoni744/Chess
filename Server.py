import socket
import rsa
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
import json

class Encryption:
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(2048)
        self.partner_public_key = None
        self.symmetric_key = None
        self.cipher = None
    
    def send_public_key(self, socket):
        socket.sendall(self.public_key.save_pkcs1('PEM'))
    
    def receive_public_key(self, socket):
        key_data = socket.recv(4096)
        self.partner_public_key = rsa.PublicKey.load_pkcs1(key_data, 'PEM')
    
    def receive_data(self, socket):
        received_payload = socket.recv(4096).decode('utf-8')
        encrypted_key, encrypted_data = received_payload.split("::")
        self.symmetric_key = rsa.decrypt(b64decode(encrypted_key), self.private_key)
        self.cipher = Fernet(self.symmetric_key)
        decrypted_data = self.cipher.decrypt(b64decode(encrypted_data))
        return json.loads(decrypted_data.decode('utf-8'))

    def generate_symmetric_key(self):
        self.symmetric_key = Fernet.generate_key()
        self.cipher = Fernet(self.symmetric_key)

    def encrypt_symmetric_key(self):
        encrypted_key = rsa.encrypt(self.symmetric_key, self.partner_public_key)
        return b64encode(encrypted_key).decode('utf-8')

    def encrypt_data(self, data):
        encrypted_data = self.cipher.encrypt(data.encode('utf-8'))
        return b64encode(encrypted_data).decode('utf-8')

def send_message(socket, encryption, data_matrix):
    encryption.generate_symmetric_key()
    serialized_data = json.dumps(data_matrix)
    encrypted_key = encryption.encrypt_symmetric_key()
    encrypted_data = encryption.encrypt_data(serialized_data)
    socket.sendall(f"{encrypted_key}::{encrypted_data}".encode('utf-8'))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(1)
encryption = Encryption()

print("\nServer started. Waiting for connections...")
connection, address = server_socket.accept()
print(f"Connected by {address}")

encryption.receive_public_key(connection)
encryption.send_public_key(connection)

# Example 2D list to send
data_matrix_to_send = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
]

send_message(connection, encryption, data_matrix_to_send)

# Receive a response or another data matrix from client
received_matrix = encryption.receive_data(connection)
print("\nReceived 2D list from client: ", received_matrix)

connection.close()
