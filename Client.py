import socket
import random

def get_host_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    return IP

def start_server(initial_port=6752):
    host_ip = get_host_ip()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    port = initial_port
    while True:
        try:
            server_socket.bind((host_ip, port))
            print(f"Server successfully bound to {host_ip}:{port}")
            break
        except socket.error as e:
            print(f"Failed to bind to {host_ip}:{port}: {e}")
            port = random.randint(1000, 9999)  # Try a new random port
            print(f"Trying new port: {port}")

    server_socket.listen(1)
    print(f"Server listening on {host_ip}:{port}")
    client_socket, addr = server_socket.accept()
    print(f"Received connection from {addr}")

    try:
        while True:
            message = input("Enter message to send: ")
            if message == "exit":
                break
            client_socket.send(message.encode())

            data = client_socket.recv(1024).decode()
            if not data:
                print("Client disconnected.")
                break
            print(f"Received from client: {data}")
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    start_server()
