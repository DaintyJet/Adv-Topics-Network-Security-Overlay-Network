from socket import socket, AF_INET, SOCK_DGRAM


class UDPServer:
    def __init__(self, port):
        """
        Args:
            port (int) - the UDP server port
        """

        self.port = port

    def start(self):
        """Listen indefinitely for UDP messages from multiple clients."""

        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))

        while True:
            message, client_addr = sock.recvfrom(1024)
            print(f'{client_addr} -> {message.decode()}')


if __name__ == '__main__':
    server = UDPServer(9999)
    server.start()
