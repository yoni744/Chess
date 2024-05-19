import socket
import threading

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Received from server: {message}")
        except:
            print("Connection lost.")
            client_socket.close()
            break

# Main client function
def client_program():
    host = "127.0.0.1"
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    # Starting a thread to receive messages
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    # Sending messages to the server
    while True:
        message = input("")
        client_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    client_program()
