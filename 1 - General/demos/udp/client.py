from socket import socket, AF_INET, SOCK_DGRAM


class UDPClient:
    def __init__(self, server, port):
        """
        Args:
            server (str) - the UDP server address
            port (int) - the UDP server port
        """

        self.server = server
        self.port = port

    def send(self, message):
        """Send a message to the server over a UDP socket.

        Args:
            message (str) - the message to send
        """

        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(message, (self.server, self.port))


if __name__ == '__main__':
    client = UDPClient('localhost', 9999)
    client.send(b'Hello Server.')
