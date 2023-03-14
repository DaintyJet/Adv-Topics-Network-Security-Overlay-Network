from json import dumps, loads
from os import urandom
from socket import socket, AF_INET, SOCK_STREAM
from xor import XOR


class AttackClient:
    def __init__(self, server, port):
        """
        Args:
            server (str) - the server address
            port (int) - the server port
        """

        self.server = server
        self.port = port

    def login(self):
        """Authenticate to the server. The protocol works as follows -
            C -> S: Login, N1
            S -> C: N2, K{N1}
            C -> S: K{N2}
            S -> C: Result
        """

        #key = open('secrets/key', 'rb').read()
        #cipher = XOR(key)

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.server, self.port))

        # Send Message - C -> S: Login, N1
        nonce1 = urandom(16)
        sock.send(dumps({'type': 'login', 'nonce1': nonce1.hex()}).encode())

        # Receive Message - S -> C: N2, K{N1}
        received = loads(sock.recv(1024))
        nonce2 = bytes.fromhex(received['nonce2'])
        enc_nonce1 = received['enc_nonce1']
        
        cipher = XOR(nonce1)

        #assert enc_nonce1 == cipher.encrypt(nonce1).hex()
        key = cipher.encrypt(bytes.fromhex(enc_nonce1))
        print(f'Response: {key}')

        # Send Message - C -> S: K{N2}
        cipher = XOR(key)
        enc_nonce2 = cipher.encrypt(nonce2).hex()
        sock.send(dumps({'enc_nonce2': enc_nonce2}).encode())

        print(f'Response: {sock.recv(512).decode()}')


if __name__ == '__main__':
    client = AttackClient(server='localhost', port=9998)
    client.login()
