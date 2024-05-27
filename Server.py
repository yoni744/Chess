import threading
import socket
import tkinter as tk

class ChessServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = []

    def start_server(self):
        print("Server started...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Client {client_address} connected")
            self.clients.append((client_socket, client_address))
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        window = tk.Tk()
        window.title(f"Chess Game with {client_address}")

        # Initialize chess board here
        board = tk.Canvas(window, width=400, height=400)
        board.pack()

        def listen_to_client():
            while True:
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break
                    # Process the received data and update the board
                except:
                    break

        threading.Thread(target=listen_to_client, daemon=True).start()
        window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(client_socket, window))
        window.mainloop()

    def on_closing(self, client_socket, window):
        client_socket.close()
        window.destroy()

if __name__ == "__main__":
    server = ChessServer('localhost', 12345)
    threading.Thread(target=server.start_server, daemon=True).start()

    tk.mainloop()  # This keeps the server running with its own Tkinter event loop
