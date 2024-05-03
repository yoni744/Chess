import socket
import random
import tkinter as tk
from tkinter import simpledialog
from threading import Thread, Event

def get_host_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    return IP

def create_display_window(host, port, close_event):
    window = tk.Tk()
    window.title("Server Information")
    window.geometry("300x100")

    tk.Label(window, text=f"Host: {host}").pack()
    tk.Label(window, text=f"Port: {port}").pack()

    def check_close_event():
        if close_event.is_set():
            window.destroy()
        else:
            window.after(100, check_close_event)  # Check again after 100ms

    window.after(100, check_close_event)
    window.mainloop()

def start_server(port=6752):
    host_ip = get_host_ip()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    while True:
        try:
            server_socket.bind((host_ip, port))
            print(f"Server successfully bound to {host_ip}:{port}")
            break
        except OSError:
            print(f"Failed to bind to {host_ip}:{port}, trying a new port...")
            port = random.randint(1000, 9999)

    close_event = Event()
    gui_thread = Thread(target=create_display_window, args=(host_ip, port, close_event))
    gui_thread.start()

    server_socket.listen(1)
    print(f"Server listening on {host_ip}:{port}")

    client_socket, addr = server_socket.accept()
    print(f"Received connection from {addr}")

    close_event.set()
    gui_thread.join()

    try:
        while True:
            message = [1, 2, 3, 4, 5,6 ,67]
            client_socket.send(message.encode())

            data = client_socket.recv(1024)
            if not data:
                print("Client disconnected.")
                break
            print("Received from client: " + data.decode())
    finally:
        client_socket.close()
        server_socket.close()

def start_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("Connected to server at {}:{}".format(host, port))

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                print("Server disconnected.")
                break
            print("Received from server: " + data.decode())

            message = input("Enter a message to send to the server: ")
            client_socket.send(message.encode())
    finally:
        client_socket.close()

def setup_network_mode():
    root = tk.Tk()
    root.title("Choose Mode")
    root.geometry("200x100")

    def server():
        root.withdraw()
        start_server()
        root.destroy()

    def client():
        root.withdraw()
        host = simpledialog.askstring("Connect to Server", "Enter the host IP:", parent=root)
        port = simpledialog.askinteger("Connect to Server", "Enter the port:", parent=root)
        if host and port:
            start_client(host, port)
        root.destroy()

    tk.Button(root, text="Server", command=server).pack(fill=tk.X)
    tk.Button(root, text="Client", command=client).pack(fill=tk.X)

    root.mainloop()

if __name__ == "__main__":
    setup_network_mode()
