import socket
import threading
import time

# Server code
class Server:
    def __init__(self, port):
        self.port = port
        self.clients = {}                                   #storing the clients
        self.lock = threading.Lock()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', self.port))
        self.sock.listen(5)

        print(f'Server listening on port {self.port}')

        while True:
            conn, addr = self.sock.accept()
            print(f'New client connected: {addr}')
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        name = conn.recv(1024).decode()
        self.clients[name] = conn

        while True:
            time.sleep(10) # Flow 2
            conn.sendall(str(self.clients.keys()).encode())

            
if __name__ == '__main__':
    server = Server(9999)
    server.start()
