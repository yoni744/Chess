import socket
import threading
import tkinter as tk

class ChessClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.window = tk.Tk()
        self.window.title("Chess Client")

        # Initialize chess board here
        self.board = tk.Canvas(self.window, width=400, height=400)
        self.board.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        threading.Thread(target=self.listen_to_server, daemon=True).start()
        self.window.mainloop()

    def listen_to_server(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                # Process the received data and update the board
            except:
                break

    def on_closing(self):
        self.client_socket.close()
        self.window.destroy()

if __name__ == "__main__":
    client = ChessClient('localhost', 12345)
