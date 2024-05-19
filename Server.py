import socket
import threading

# Global list to keep track of connected clients and their addresses
clients = []

# Function to handle client connection
def handle_client(client_socket, client_address):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                print(f"Message from {client_address}: {message.decode('utf-8')}")
                broadcast(message, client_socket)
            else:
                remove(client_socket)
                break
        except:
            continue

# Function to broadcast a message to all clients
def broadcast(message, client_socket):
    for client in clients:
        if client[0] != client_socket:
            try:
                client[0].send(message)
            except:
                remove(client[0])

# Function to remove a client from the list
def remove(client_socket):
    for client in clients:
        if client[0] == client_socket:
            clients.remove(client)
            break

# Main server function
def server_program():
    host = "127.0.0.1"
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started on {host}:{port}")

    # Accepting clients
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append((client_socket, client_address))
        print(f"Connection from {client_address}")

        # Starting a new thread for each client
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

        # Allow server to send messages to clients
        threading.Thread(target=server_send, args=(server_socket,)).start()

# Function for server to send messages
def server_send(server_socket):
    while True:
        message = input("")
        broadcast(message.encode('utf-8'), server_socket)

if __name__ == "__main__":
    server_program()
